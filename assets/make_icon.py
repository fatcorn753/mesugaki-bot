# アイコン(assets/icon.png, 1024px)を描く。実行には Pillow が要る: .venv/bin/pip install pillow
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S=1024
im=Image.new("RGBA",(S,S),(0,0,0,0))
d=ImageDraw.Draw(im)
# 背景: ピンクのグラデーション
bg=Image.new("RGBA",(S,S))
bd=ImageDraw.Draw(bg)
for y in range(S):
    t=y/S
    bd.line([(0,y),(S,y)],fill=(int(255-20*t),int(182-60*t),int(214-30*t),255))
im.alpha_composite(bg)
d=ImageDraw.Draw(im)
HAIR=(120,60,160); HAIR2=(150,85,190); SKIN=(255,233,220); LINE=(70,35,70)
# ツインテール
d.ellipse([60,330,330,900],fill=HAIR)
d.ellipse([694,330,964,900],fill=HAIR)
# 後ろ髪
d.ellipse([190,170,834,880],fill=HAIR)
# 顔
d.ellipse([250,290,774,820],fill=SKIN)
# 前髪(ぎざぎざ)
d.chord([230,160,794,660],180,360,fill=HAIR2)
for i,x0 in enumerate(range(262,700,83)):
    d.polygon([(x0-4,405),(x0+87,405),(x0+42,490+(i%2)*25)],fill=HAIR2)
# リボン
for cx in (210,814):
    d.polygon([(cx,330),(cx-80,260),(cx-80,400)],fill=(255,80,140))
    d.polygon([(cx,330),(cx+80,260),(cx+80,400)],fill=(255,80,140))
    d.ellipse([cx-28,302,cx+28,358],fill=(230,50,110))
# 目: 半目のジト目(上まぶたが平ら)
for ex in (390,634):
    d.ellipse([ex-62,540,ex+62,660],fill=(255,255,255))
    d.ellipse([ex-40,560,ex+40,660],fill=(230,60,140))
    d.ellipse([ex-18,585,ex+18,640],fill=(120,20,70))
    d.ellipse([ex-4,575,ex+20,600],fill=(255,255,255))
    d.rectangle([ex-70,500,ex+70,575],fill=SKIN)  # まぶたで上を隠す
    d.line([ex-72,575,ex+72,568],fill=LINE,width=14)
# 眉(ニヤつき)
d.line([320,500,450,520],fill=LINE,width=10)
d.line([574,520,704,500],fill=LINE,width=10)
# ほっぺ
blush=Image.new("RGBA",(S,S),(0,0,0,0)); bdd=ImageDraw.Draw(blush)
bdd.ellipse([300,660,420,720],fill=(255,120,150,150)); bdd.ellipse([604,660,724,720],fill=(255,120,150,150))
im.alpha_composite(blush.filter(ImageFilter.GaussianBlur(12)))
d=ImageDraw.Draw(im)
# 口: 片側上がりのにやり + 八重歯
d.arc([450,640,610,740],15,150,fill=LINE,width=12)
d.line([598,712,625,690],fill=LINE,width=12)
d.polygon([(560,733),(582,729),(574,760)],fill=(255,255,255),outline=LINE)
# ハート
import math
pts=[]
for k in range(200):
    t=2*math.pi*k/200
    x=16*math.sin(t)**3; y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
    pts.append((800+x*5.5,730-y*5.5))
d.polygon(pts,fill=(255,60,130),outline=(255,255,255),width=12)
im=im.convert("RGB")
im.save("assets/icon.png")
