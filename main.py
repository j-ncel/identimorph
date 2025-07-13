import streamlit as st
from identimorph.identimorph import identimorph, identimorph_spiral
from io import BytesIO


class NamedBytesIO(BytesIO):
    def __init__(self, name):
        super().__init__()
        self.name = name


st.set_page_config(page_title="Identimorph Generator",
                   page_icon="🏁", layout="centered")

st.title("🏁 Identimorph Generator")
st.write(":blue[Transform text into animated identicons.]")

maincol = st.columns(2)


with maincol[0]:
    with st.container(border=True):
        text = st.text_input("Enter Text", value="jncel")
        style = st.radio("Animation Style", [
                         "Classic", "Spiral"], horizontal=True)

        settingcol = st.columns(2)
        size = settingcol[0].number_input("Canvas Size (px)", min_value=64,
                                          max_value=512, value=256, step=16)
        fps = settingcol[1].number_input("FPS", min_value=1,
                                         max_value=30, value=5)
        glow = settingcol[0].number_input("Glow", min_value=0,
                                          max_value=10, value=0)

        if style == "Classic":
            frames = settingcol[1].number_input("Frame Count", min_value=1,
                                                max_value=64, value=8, step=1)
            blocks = None
        else:
            blocks = settingcol[1].number_input("Block Count", min_value=3,
                                                max_value=10, value=5, step=1)
            frames = None

with maincol[1]:
    buffer = NamedBytesIO(f"{text}_{style.lower()}.gif")

    if style == "Spiral":
        identimorph_spiral(
            text=text,
            blocks=blocks,
            size=size,
            glow=glow,
            fps=fps,
            output_path=buffer
        )
    else:
        identimorph(
            text=text,
            frames=frames,
            size=size,
            glow=glow,
            fps=fps,
            output_path=buffer
        )

    buffer.seek(0)
    st.image(buffer, caption=f"Preview: '{text}' ({style})", width=size)
    st.download_button(
        label="🔻 Download GIF",
        data=buffer.getvalue(),
        file_name=f"{text}_{style.lower()}.gif",
        mime="image/gif"
    )

st.markdown("""
<a href="https://coff.ee/jncel" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" width="140">
</a>
""", unsafe_allow_html=True)
