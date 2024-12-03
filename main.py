import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import json, math, os
from decimal import Decimal as de
import dotenv

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="@", intents=intents)
dotenv.load_dotenv()


def parse_complex(value):

    if "," in value:
        parts = value.split(",")
        re = de(parts[0])
        im = de(parts[1])
        return complex(re, im)
    else:
        return de(value)


def infinity_list(n_start, k):
    i = n_start - k
    while True:
        i += k
        yield i


@bot.hybrid_command(name="使用說明", description="取得「繪製圖表」的輸入資訊")
async def help_(ctx: discord.Interaction):
    embed = discord.Embed(title="使用說明")
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1248158691753070623/1299187312323727432/1131548579513765928.png?ex=671c49f8&is=671af878&hm=2b4a36d19bed80319c1d7d5a909f0712ec4aeebdaa93b0610efa1795cff037f0&=&format=webp&quality=lossless&width=1410&height=182"
    )
    embed.add_field(name="n的起始值", value="輸入n的起始數值", inline=True)
    embed.add_field(name="n的項數", value="輸入n的項數", inline=True)
    embed.add_field(name="n的遞增值", value="輸入n的遞增值", inline=True)
    embed.add_field(
        name="輸入參數",
        value="依序輸入`p1 q1 p2 q2 r1 r2`，複數`a+bi`請用```a,b```表示",
        inline=True,
    )
    embed.add_field(
        name="是否在電腦上顯示(選填)",
        value="將圖片顯示於電腦上以方便放大縮小",
        inline=False,
    )
    embed.add_field(
        name="檔案名稱", value="設定檔案標題與儲存於電腦上的檔案名稱", inline=True
    )
    await ctx.send(embed=embed)


@bot.hybrid_command(name="繪製圖表", description="輸入參數以繪製(p1 q1 p2 q2 r1 r2)")
async def draw(
    ctx: discord.Interaction,
    n的起始值: float,
    n的項數: int,
    n的遞增值: float,
    輸入參數: str,
    是否在電腦上顯示: bool = False,
    檔案名稱: str = None,
):
    if 檔案名稱 == None:
        檔案名稱 = 輸入參數
    n_start = n的起始值
    n_len = n的項數
    k = n的遞增值
    __n__ = infinity_list(n_start, k=k)

    # 輸入參數
    input_num = 輸入參數.split()
    if len(input_num) != 6:
        await ctx.send("參數格式錯誤")
        return
    r1, r2 = (
        input_num[4],
        input_num[5],
    )
    try:
        p1, q1, p2, q2 = (
            de(input_num[0]),
            de(input_num[1]),
            de(input_num[2]),
            de(input_num[3]),
        )
    except:
        await ctx.send("`p1 q1 p2 q2`不為複數")
        return

    r1 = parse_complex(r1)
    r2 = parse_complex(r2)

    # 定義函式
    a1 = complex(float(p1), float(q1))
    a2 = complex(float(p2), float(q2))

    alpha = ((complex(r1)) + ((complex(r1)) ** 2 + 4 * complex(r2)) ** 0.5) / 2
    beta = ((complex(r1)) - ((complex(r1)) ** 2 + 4 * complex(r2)) ** 0.5) / 2

    with open(os.path.dirname(__file__) + "\\data.json", "r") as data:
        an_json = json.load(data)
    an_json[輸入參數 + " %d %d %f" % (n_start, n_len, k)] = {}

    an = []
    an_x = []
    an_y = []

    an_tangle = []
    an_r = []
    loading_icon = ["▗", "▖", "▘", "▝"]

    message = await ctx.send(r"\| " + " " * 25 + f" | 0/{n_len} [  0%] ▝")

    for i in range(n_len):
        await message.edit(
            content=rf"\| {'▮'*int(((i+1)/n_len)*25)+'　'*(25-int(((i+1)/n_len)*25))} | {i+1}/{n_len} [{int(((i+1)/n_len)*100):3d}%] {loading_icon[i%4]}"
        )

        n = next(__n__)

        an.append(
            (1 / (alpha - beta))
            * (
                complex(float(a2.real), float(a2.imag))
                * (alpha ** (n - 1) - beta ** (n - 1))
                + complex(r2)
                * complex(float(a1.real), float(a1.imag))
                * (alpha ** (n - 2) - beta ** (n - 2))
            )
        )

        an_x.append([an[-1].real, "r" if round(n, 4) % 1 == 0 else "b"])
        an_y.append(an[-1].imag)

        # tangle
        r = math.sqrt(de(an[-1].real) ** 2 + de(an[-1].imag) ** 2)
        theta = math.atan2(an[-1].imag, an[-1].real) * 180 / math.pi
        an_tangle.append(theta)
        an_r.append(r)

        # save data

        an_json[輸入參數 + " %d %d %f" % (n_start, n_len, k)][f"{n:.3f}"] = str(
            an[-1]
        ).replace("(", "").replace(")", "").replace("j", "i") + " %.6f %.6f" % (
            theta,
            r,
        )

    # 繪製圖表 [[x, color], [x, color]]
    await message.edit(content="complete!, plotting...")

    plt.figure(輸入參數)
    plt.title(輸入參數 if 檔案名稱 != None else 檔案名稱)
    for x in range(len(an_x)):
        plt.scatter(an_x[x][0], an_y[x], color=an_x[x][1])
    plt.savefig(os.path.dirname(__file__) + "\\result\\" + 檔案名稱 + ".png")

    plt.figure("ln")
    plt.title("ln")
    for i in range(len(an)):
        plt.scatter(
            (
                math.log(abs(an[i].real), math.e) * (-1 if an[i].real < 0 else 1)
                if an[i].real > 0
                else 0
            ),
            (
                math.log(abs(an[i].imag), math.e) * (-1 if an[i].imag < 0 else 1)
                if an[i].imag > 0
                else 0
            ),
            color=an_x[i][1],
        )
    plt.savefig(os.path.dirname(__file__) + "\\result\\" + 檔案名稱 + "ln" + ".png")

    with open(
        os.path.dirname(__file__) + "\\data.json",
        "w",
        encoding="utf-8",
    ) as data:
        json.dump(an_json, data, indent=4)

    file = [
        discord.File(os.path.dirname(__file__) + "\\result\\" + 檔案名稱 + ".png"),
        discord.File(
            os.path.dirname(__file__) + "\\result\\" + 檔案名稱 + "ln" + ".png"
        ),
    ]

    # 編輯訊息並附上圖片
    await message.edit(content="complete! Plotting finished.", attachments=file)
    if 是否在電腦上顯示 and ctx.guild.id == 1245924697523097682:
        msg = await ctx.send("已在電腦上顯示，機器人暫停運行")
        plt.show()
        await msg.edit(content="機器人已正常運行")
    else:
        await ctx.send("訪客身分不開放`是否在電腦上顯示`功能")
    plt.close("all")


@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f">> {bot.user} <<")
    print(f"載入 {len(slash)} 個斜線指令")


bot.run(os.getenv("TOKEN"))
