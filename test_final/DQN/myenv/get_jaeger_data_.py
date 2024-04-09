import requests
import json

def query_jaeger_api(url, query_params):
    try:
        response = requests.get(url, params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("请求失败:", str(e))
        return None

def save_to_json(data, file_path):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print("结果已保存到:", file_path)
    except IOError as e:
        print("保存文件时出错:", str(e))

def main():
    # Jaeger的API地址
    jaeger_url = "http://172.19.206.70:16686/api/traces"

    # 查询参数
    # services = [
    #     "home-timeline-service",
    #     "media-service"
    # ]

    query_params = {
        "service": "home-timeline-service",
        "service": "media-service",
        "service": "nginx-web-server",
        "service": "text-service",
        "service": "user-timeline-service",
        # "service": "nginx-web-server",
        # "service": "compose-post-service",
        
        # "service": "url-shorten-service",
        # "service": "post-storage-service",
        # "service": "unique-id-service",
   
        "limit": 10
    }

    # 发送查询请求
    traces = query_jaeger_api(jaeger_url, query_params)

    # 将结果保存到JSON文件
    if traces:
        file_path = "jaeger_traces.json"
        save_to_json(traces, file_path)

if __name__ == "__main__":
    main()