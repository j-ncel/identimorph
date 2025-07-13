import streamlit as st
from identimorph.identimorph import identimorph
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
    with st.form(key="identimorph_form"):
        text = st.text_input("Enter Text", value="jncel")
        settingcol = st.columns(2)

        size = settingcol[0].number_input("Canvas Size (px)", min_value=64,
                                          max_value=512, value=256, step=16)
        frames = settingcol[1].number_input("Frame Count", min_value=1,
                                            max_value=64, value=8, step=1)
        fps = settingcol[0].number_input("FPS", min_value=1,
                                         max_value=30, value=1)
        glow = settingcol[1].number_input(
            "Glow", min_value=0, max_value=10, value=0)

        generate = st.form_submit_button("✨ Generate")

with maincol[1]:
    preview = st.container()
    with preview:
        if generate:
            buffer = NamedBytesIO("identimorph.gif")
            identimorph(
                text=text,
                frames=frames,
                size=size,
                glow=glow,
                fps=fps,
                output_path=buffer
            )
            buffer.seek(0)

            st.image(buffer, caption=f"Preview: '{text}'", width=size)
            st.download_button(
                label="🔻 Download GIF",
                data=buffer.getvalue(),
                file_name=f"{text}_identimorph.gif",
                mime="image/gif"
            )
        else:
            with open("sample/jncel_identimorph.gif", "rb") as file:
                default_gif = file.read()
                st.image(
                    default_gif, caption="Default Preview: 'jncel'", width=256)
                st.download_button(
                    label="🔻   Download GIF",
                    data=default_gif,
                    file_name=f"{text}_identimorph.gif",
                    mime="image/gif"
                )

st.markdown("""
<a href="https://coff.ee/jncel" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" width="140">
</a>
""", unsafe_allow_html=True)
