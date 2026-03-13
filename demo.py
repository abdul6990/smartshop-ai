from dotenv import load_dotenv
load_dotenv()
from utils.auth import request_otp
result = request_otp('neelsyedabdulrehaman@gmail.com')
print(result)