from openai import OpenAI
import base64


class ImageDescriptionService:
    def __init__(self):
        self.client = OpenAI(api_key="api_key")
        self.reference_images = self._load_reference_images()
        
    def _load_reference_images(self):
        """預先載入所有參考圖片"""
        reference_images = {}
        try:
            with open("example/liftcar_scissor.jpg", "rb") as ref1, \
                 open("example/liftcar.jpg", "rb") as ref2, \
                 open("example/excavator.jpg", "rb") as ref3, \
                 open("example/crane.jpg", "rb") as ref4:
                
                reference_images = {
                    "scissor_lift": base64.b64encode(ref1.read()).decode(),
                    "boom_lift": base64.b64encode(ref2.read()).decode(),
                    "excavator": base64.b64encode(ref3.read()).decode(),
                    "crane": base64.b64encode(ref4.read()).decode()
                }
            return reference_images
        except Exception as e:
            print(f"載入參考圖片時發生錯誤: {str(e)}")
            return None

    def generate_description(self, image_path):
        """生成圖片描述"""
        try:
            with open(image_path, "rb") as image_file:
                messages_content = [
                    {
                        "type": "text",
                        "text": "以下是標準工地機具的參考圖片，請記住這些機具的特徵："
                    }
                ]
                
                # 添加參考圖片及說明
                reference_descriptions = {
                    "scissor_lift": "1. 剪刀式高空作業車（Scissor Lift）：",
                    "boom_lift": "2. 直臂式高空作業車（Boom Lift）：",
                    "excavator": "3. 挖土機（Excavator）：",
                    "crane": "4. 吊臂車（Crane）："
                }
                
                for key, description in reference_descriptions.items():
                    messages_content.extend([
                        {
                            "type": "text",
                            "text": description
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.reference_images[key]}"
                            }
                        }
                    ])
                
                # 添加分析要求和目標圖片
                messages_content.extend([
                    {
                        "type": "text",
                        "text": "根據以上參考圖片的機具特徵，請分析下面這張施工現場的圖片，著重於：\n1. 工人的安全裝備（安全帽、反光背心、背負式安全帶）是否符合規範\n2. 機具的使用\n請在100個字內完成描述。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
                        }
                    }
                ])
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一個專業的工地安全檢查員，專門負責檢查工地的安全設備與機具使用情況。"
                        },
                        {
                            "role": "user",
                            "content": messages_content
                        }
                    ],
                    max_tokens=150
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"生成描述時發生錯誤: {str(e)}")
            return None