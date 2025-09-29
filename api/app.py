import requests
import uuid
from typing import List, Dict, Any
from flask import Flask, request, jsonify

app = Flask(__name__)

class TMTReaderAPI:
    def __init__(self):
        self.base_url = "https://api.tmtreader.com"
        self.common_headers = {
            "Host": "api.tmtreader.com",
            "Accept": "application/json; charset=utf-8,application/x-protobuf",
            "X-Xs-From-Web": "false",
            "Age-Range": "8",
            "Sdk-Version": "2",
            "Passport-Sdk-Version": "50357",
            "X-Vc-Bdturing-Sdk-Version": "2.2.1.i18n",
            "User-Agent": "com.worldance.drama/49819 (Linux; U; Android 9; in; SM-N976N; Build/QP1A.190711.020;tt-ok/3.12.13.17)",
        }
        self.common_params = {
            "iid": "7549249992780367617",
            "device_id": "6944790948585719298",
            "ac": "wifi",
            "channel": "gp",
            "aid": "645713",
            "app_name": "Melolo",
            "version_code": "49819",
            "version_name": "4.9.8",
            "device_platform": "android",
            "os": "android",
            "ssmix": "a",
            "device_type": "SM-N976N",
            "device_brand": "samsung",
            "language": "in",
            "os_api": "28",
            "os_version": "9",
            "openudid": "707e4ef289dcc394",
            "manifest_version_code": "49819",
            "resolution": "900*1600",
            "dpi": "320",
            "update_version_code": "49819",
            "current_region": "CN",
            "carrier_region": "ID",
            "app_language": "id",
            "sys_language": "in",
            "app_region": "CN",
            "sys_region": "ID",
            "mcc_mnc": "46002",
            "carrier_region_v2": "460",
            "user_language": "id",
            "time_zone": "Asia/Bangkok",
            "ui_language": "in",
            "cdid": "a854d5a9-b6cd-4de7-9c43-8310f5bf513c",
        }

    def _generate_rticket(self) -> str:
        """Generate a unique rticket."""
        return str(int(uuid.uuid1().int >> 64))

    def search_novels(self, query: str, offset: str = "0", limit: str = "10") -> Dict[str, Any]:
        """Search novels based on query and return extracted book information."""
        url = f"{self.base_url}/i18n_novel/search/page/v1/"
        headers = self.common_headers.copy()
        params = self.common_params.copy()
        params.update({
            "search_source_id": "clks###",
            "IsFetchDebug": "false",
            "offset": offset,
            "cancel_search_category_enhance": "false",
            "query": query,
            "limit": limit,
            "search_id": "",
            "_rticket": self._generate_rticket(),
        })
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return {"status_code": response.status_code, "books": []}
        
        json_data = response.json()
        books = self._extract_books_from_search(json_data)
        return {"status_code": response.status_code, "books": books}

    def _extract_books_from_search(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract book_id, book_name, last_chapter_index, and thumb_url from search response."""
        books = []
        search_data = json_data.get("data", {}).get("search_data", [])
        
        for item in search_data:
            item_books = item.get("books", [])
            for book in item_books:
                book_info = {
                    "series_id": book.get("book_id", ""),
                    "title": book.get("book_name", ""),
                    "last_chapter_index": book.get("last_chapter_index", ""),
                    "thumb_url": book.get("thumb_url", "")
                }
                books.append(book_info)
        
        return books

    def get_video_details(self, series_id: str) -> Dict[str, Any]:
        """Get video details for a specific series and return extracted video information."""
        url = f"{self.base_url}/novel/player/video_detail/v1/"
        headers = self.common_headers.copy()
        headers.update({
            "X-Ss-Stub": "238B6268DE1F0B757306031C76B5397E",
            "Content-Encoding": "gzip",
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": "157",
        })
        params = self.common_params.copy()
        params["_rticket"] = self._generate_rticket()
        
        data = {
            "biz_param": {
                "detail_page_version": 0,
                "from_video_id": "",
                "need_all_video_definition": False,
                "need_mp4_align": False,
                "source": 4,
                "use_os_player": False,
                "video_id_type": 1
            },
            "series_id": series_id
        }
        
        response = requests.post(url, headers=headers, params=params, json=data)
        
        if response.status_code != 200:
            return {"status_code": response.status_code, "videos": []}
        
        json_data = response.json()
        videos = self._extract_videos_from_details(json_data)
        return {"status_code": response.status_code, "videos": videos}

    def _extract_videos_from_details(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract duration, digged_count, vid, and vid_index from video details response."""
        videos = []
        video_list = json_data.get("data", {}).get("video_data", {}).get("video_list", [])
        
        for video in video_list:
            video_info = {
                "duration": video.get("duration", 0),
                "digged_count": video.get("digged_count", 0),
                "video_id": video.get("vid", ""),
                "chapter": video.get("vid_index", "")
            }
            videos.append(video_info)
        
        return videos

    def get_video_model(self, video_id: str) -> Dict[str, Any]:
        """Get video model information and return extracted URL information."""
        url = f"{self.base_url}/novel/player/video_model/v1/"
        headers = self.common_headers.copy()
        headers.update({
            "X-Ss-Stub": "B7FB786F2CAA8B9EFB7C67A524B73AFB",
            "Content-Encoding": "gzip",
            "Content-Type": "application/json; charset=utf-8",
        })
        params = self.common_params.copy()
        params["_rticket"] = self._generate_rticket()
        
        data = {
            "biz_param": {
                "detail_page_version": 0,
                "device_level": 3,
                "from_video_id": "",
                "need_all_video_definition": True,
                "need_mp4_align": False,
                "source": 4,
                "use_os_player": False,
                "video_id_type": 0,
                "video_platform": 3
            },
            "video_id": video_id
        }
        
        response = requests.post(url, headers=headers, params=params, json=data)
        
        if response.status_code != 200:
            return {"status_code": response.status_code, "video_urls": {}}
        
        json_data = response.json()
        video_urls = self._extract_video_urls(json_data)
        return {"status_code": response.status_code, "video_urls": video_urls}

    def _extract_video_urls(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract backup_url and main_url from video model response."""
        data = json_data.get("data", {})
        return {
            "backup_url": data.get("backup_url", ""),
            "main_url": data.get("main_url", "")
        }

# Initialize TMTReaderAPI
tmt_api = TMTReaderAPI()

@app.route('/api/search', methods=['GET'])
def search_novels():
    """API endpoint to search novels."""
    query = request.args.get('query', default='super keren', type=str)
    offset = request.args.get('offset', default='0', type=str)
    limit = request.args.get('limit', default='10', type=str)
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    result = tmt_api.search_novels(query=query, offset=offset, limit=limit)
    return jsonify(result)

@app.route('/api/video-details', methods=['GET'])
def get_video_details():
    """API endpoint to get video details for a series."""
    series_id = request.args.get('series_id', type=str)
    
    if not series_id:
        return jsonify({"error": "series_id parameter is required"}), 400
    
    result = tmt_api.get_video_details(series_id=series_id)
    return jsonify(result)

@app.route('/api/video-model', methods=['GET'])
def get_video_model():
    """API endpoint to get video model information."""
    video_id = request.args.get('video_id', type=str)
    
    if not video_id:
        return jsonify({"error": "video_id parameter is required"}), 400
    
    result = tmt_api.get_video_model(video_id=video_id)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
