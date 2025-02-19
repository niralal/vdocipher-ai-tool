import requests
import subprocess

class VdoCipherClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://dev.vdocipher.com/api"
        self.headers = {"Authorization": f"Apisecret {api_key}"}
        self.ffmpeg_path = "/usr/local/bin/ffmpeg"  # For macOS

    def get_video_info(self, video_id):
        url = f"{self.base_url}/videos/{video_id}/files"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Video info response status: {response.status_code}")
            print(f"Video info response content: {response.text}")
        return response.json() if response.status_code == 200 else None

    def get_download_url(self, video_id, file_id):
        """Get the download URL for a specific file ID"""
        try:
            url = f"{self.base_url}/videos/{video_id}/files/{file_id}"
            print(f"Requesting file download info from: {url}")
            
            response = requests.get(url, headers=self.headers)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                url = data.get("redirect")
                print(f"Got URL: {url}")
                return url
            
            return None
        except Exception as e:
            print(f"Error in get_download_url: {str(e)}")
            return None

    def download_file(self, file_url, output_path, extract_audio=False):
        try:
            # Regular file download using requests
            response = requests.get(file_url, stream=True)
            print(f"Download response status: {response.status_code}")
            
            if response.status_code == 200:
                with open(output_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                return output_path
            else:
                print(f"Download failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None

    def upload_subtitle(self, video_id, subtitle_path, language):
        """
        Upload subtitle file for a video using VdoCipher API.
        
        Args:
            video_id (str): The video ID
            subtitle_path (str): Path to the subtitle file
            language (str): ISO 639-1 language code (e.g. 'he', 'ar')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"https://dev.vdocipher.com/api/videos/{video_id}/files/"
            
            # Prepare the multipart form data
            files = {
                'file': open(subtitle_path, 'rb')
            }
            
            # Add language as query parameter
            params = {
                'language': language
            }
            
            # Make the request
            response = requests.post(
                url,
                params=params,
                files=files,
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"Successfully uploaded {language} subtitles")
                return True
            
            print(f"Failed to upload subtitles: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"Error uploading subtitles: {str(e)}")
            return False

    def print_video_info(self, video_info):
        """Pretty print video file information"""
        if not isinstance(video_info, list):
            print("No video information available")
            return

        print("\n=== Video Files ===")
        for item in video_info:
            print(f"\n📄 File: {item.get('name', 'Unnamed')}")
            print("   " + "─" * 40)
            
            # Main properties
            print(f"   📌 ID: {item.get('id')}")
            print(f"   📦 Size: {item.get('size', 0) / 1024 / 1024:.2f} MB")
            print(f"   🔒 Encryption: {item.get('encryption_type', 'none')}")
            
            # Media properties
            if item.get('video_codec') or item.get('audio_codec'):
                print("   🎥 Media Info:")
                if item.get('video_codec'):
                    print(f"      • Video: {item['video_codec']} ({item.get('width', '?')}x{item.get('height', '?')})")
                if item.get('audio_codec'):
                    print(f"      • Audio: {item['audio_codec']}")
                if item.get('bitrate'):
                    print(f"      • Bitrate: {item['bitrate']} kbps")
            
            # Stream information
            if item.get('params', {}).get('streams'):
                print("   🌊 Streams:")
                for stream in item['params']['streams']:
                    stream_type = "🔊" if stream.get('contentType') == 'audio' else "🎬"
                    print(f"      {stream_type} {stream.get('mimeType', '?')} "
                          f"({stream.get('bandwidth', '?')} bps)")
            
            # Access flags
            flags = []
            if item.get('isDownloadable'):
                flags.append("⬇️ Downloadable")
            if item.get('isDeletable'):
                flags.append("🗑️ Deletable")
            if flags:
                print("   " + " | ".join(flags))
