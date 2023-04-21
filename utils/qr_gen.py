import os
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import ImageColorMask
from utils.generate import generate_client
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


def generate_qr(tlg, name):
    logo = Image.open(os.path.join(os.getcwd(), "img", "logo.png")).resize((70, 70))
    back = Image.open(os.path.join(os.getcwd(), "img", "back.jpg"))

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2,
    )
    config = generate_client(tlg, name)
    qr.add_data(config)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=ImageColorMask(back_color=(255, 255, 255), color_mask_image=back),
    )

    logo_x_position = (img.size[0] - logo.size[0]) // 2
    logo_y_position = (img.size[1] - logo.size[1]) // 2
    logo_position = (logo_x_position, logo_y_position)

    img.paste(logo, logo_position, logo.convert('RGBA'))
    # img.save(os.path.join(os.getenv("CLIENT_CONF_DIR"), f"qrcode-{name}.png"))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
