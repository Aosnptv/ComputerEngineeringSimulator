"""Font selection for the standalone tester only; shared language is untouched."""
from pathlib import Path
from panda3d.core import Filename

def resolve_font(loader,requested=None):
 candidates=[requested] if requested else []
 candidates += ['C:/Windows/Fonts/tahoma.ttf','C:/Windows/Fonts/leelawui.ttf',
                'C:/Windows/Fonts/LeelawUI.ttf',
                '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf']
 for name in candidates:
  if not name or not Path(name).is_file():continue
  try:
   font=loader.load_font(Filename.from_os_specific(str(Path(name).resolve())))
   if font and all(font.has_character(ord(c)) for c in 'กาำีเ้'):return str(Path(name).resolve())
  except (OSError,TypeError):continue
 return None
