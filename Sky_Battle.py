import math
import os
import random
import sys
import time
import pygame as pg
import pygame

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm

class HpGauge:
    """
    HPゲージに関するクラス
    """
    def __init__(self):
        self.max_hp = 10  # HPの最大を10に設定
        self.now_hp = self.max_hp  # 現在のHPを最大のHPに初期化
        self.empty_color = (128, 128, 128)  # 空のゲージを灰色に設定
        self.now_color = (0, 255, 0)  # 現在のゲージを緑色に設定
        self.max_hight = 20  # ゲージの高さを20に設定
        self.max_width = 200  # ゲージの幅を200に設定

    def decrease(self, damage):  # 被弾でゲージを減らす関数
        self.now_hp = max(0, self.now_hp - damage)  # 受けたダメージ分、現在のHPを減らす。ただし、0未満にはならない。
        if self.now_hp <= self.max_hp * 0.2:  # もし現在のHPが最大のHPの20%以下になったら
            self.now_color = (255, 0, 0)  # 現在のゲージの色を赤色に設定
        elif self.now_hp <= self.max_hp * 0.4:  # もし現在のHPが最大のHPの40%以下になったら
            self.now_color = (255, 255, 0)  # 現在のゲージの色を黄色に設定
        return self.now_hp == 0  # HPが0になったら、負け判定のTrueを返す

    def update(self, screen: pg.Surface):
        now_width = (self.now_hp / self.max_hp) * self.max_width  # 現在のゲージの幅を、現在のHPに応じて計算
        pg.draw.rect(screen, self.empty_color, [WIDTH - 220, 20, self.max_width, self.max_hight])  # 空のゲージを描画
        pg.draw.rect(screen, self.now_color, [WIDTH - 220, 20, now_width, self.max_hight])  # 現在のゲージを描画

class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = 10
        self.move = "neutral"

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
            
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.move = "move"
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        else:
            self.move = "neutral"
        if self.state == "hyper":
            self.speed = 20
            self.hyper_life -= 1
        if self.hyper_life < 0:
            self.speed = 10
            self.state = "normal"
            self.hyper_life = 10
        
        screen.blit(self.image, self.rect)

class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    def __init__(self, emy: "Enemy", bird: Bird, bomb_type=0):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        引数3 bomb_type：爆弾の種類（0: 打てる, 1: 打てない）
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6
        self.type = bomb_type  # 0: shootable, 1: non-shootable

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()
    
    def bomb_check(self):
        self.kill()

class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, start_pos, target_pos):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.Surface((20, 20))
        color = (0, 0, 255)  
        pg.draw.circle(self.image, color, (10, 10), 10)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.target_pos = target_pos
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        angle = math.atan2(dy, dx)
        self.vel_x = math.cos(angle) * self.speed
        self.vel_y = math.sin(angle) * self.speed

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        # 弾を移動
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if check_bound(self.rect) != (True, True):
            self.kill()
    
class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(random.choice(__class__.imgs), 0, 0.8)
        self.rect = self.image.get_rect()
        # 出現位置を画面内に限定
        self.rect.center = (
            random.randint(self.rect.width // 2, WIDTH - self.rect.width // 2),
            random.randint(self.rect.height // 2, HEIGHT // 4),
        )
        self.vx, self.vy = random.choice([-3, -2, -1, 1, 2, 3]), +6
        self.bound = random.randint(50, HEIGHT - 50)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル
        self.max_hp = 10   # 敵のHPの最大を10に設定
        self.now_hp = self.max_hp  # 敵の現在のHPを最大のHPに初期化
        self.empty_color = (128, 128, 128)  # 空のゲージを灰色に設定
        self.now_color = (0, 255, 0)   # 現在のゲージを緑色に設定

    def decrease(self, damage):   # 敵のゲージを減らす関数
        self.now_hp = max(0, self.now_hp - damage)  # 受けたダメージ分、現在のHPを減らす。ただし、0未満にはならない。
        if self.now_hp <= self.max_hp * 0.2:  # もし現在のHPが最大のHPの20%以下になったら
            self.now_color = (255, 0, 0)  # 現在のゲージの色を赤色に設定
        elif self.now_hp <= self.max_hp * 0.4:  # もし現在のHPが最大のHPの40%以下になったら
            self.now_color = (255, 255, 0)  # 現在のゲージの色を黄色に設定
        return self.now_hp == 0  # HPが0になったら、撃破判定のTrueを返す

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        """
        if self.state == "down":
            self.rect.move_ip(self.vx, self.vy)
            # 画面外にはみ出さないように制御
            yoko, tate = check_bound(self.rect)
            if not yoko:
                self.vx *= -1  # 横方向の移動を反転
            if self.rect.centery > self.bound:
                self.vy = 0
                self.state = "stop"
        now_width = (self.now_hp / self.max_hp) * self.rect.width  # 現在のゲージの幅を、現在のHPに応じて計算
        pg.draw.rect(pg.display.get_surface(), self.empty_color, [self.rect.x, self.rect.y - 10, self.rect.width, 5])  # 空のゲージを描画
        pg.draw.rect(pg.display.get_surface(), self.now_color, [self.rect.x, self.rect.y - 10, now_width, 5])  # 現在のゲージを描画

class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font("font/BebasNeue-Regular.ttf", 40)
        self.text_color = (0, 0, 0)  # 文字の色
        self.bg_color = (255, 255, 255)  # 四角形の背景色（白）
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.text_color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH // 2, 30  # 表示位置を画面中央（幅）に調整

    def update(self, screen: pg.Surface, Enemy_num, count_ProSpirit, tmr):
        """
        スコアの更新と描画を行うメソッド
        引数：
          - screen: 描画対象のSurface
          - Enemy_num: 敵機の数
          - count_ProSpirit: 実行までのカウント
        """
        # 更新されたスコア文字列を生成
        text = f"{self.value:05} Pt  Time:{tmr//60:03} {Enemy_num:03} {count_ProSpirit}"
        self.image = self.font.render(text, True, self.text_color)
        self.rect = self.image.get_rect()  # 新しいサイズに合わせてRectを更新
        self.rect.center = WIDTH // 2, 35  # 表示位置を再設定

        # 四角形の大きさを文字サイズに基づいて設定
        padding_x = 20  # テキストの周囲の余白
        padding_y = 5
        bg_rect = pg.Rect(
            self.rect.x - padding_x,
            self.rect.y - padding_y,
            self.image.get_width() + 2 * padding_x,
            self.image.get_height() + 2 * padding_y,
        )
        # 背景用の透明なSurfaceを作成
        bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        pg.draw.rect(bg_surface, (255, 255, 255, 200), bg_surface.get_rect(), border_radius=15)# 丸角の四角形を背景Surfaceに描画
        screen.blit(bg_surface, (bg_rect.x, bg_rect.y))# 背景Surfaceをメイン画面に描画
        screen.blit(self.image, self.rect)# 文字を描画

def gameover(screen: pg.Surface) -> None:
    clock = pg.time.Clock()
    alpha = 0  # 背景フェードイン用
    fade_speed = 5  # フェード速度
    # 背景色の赤いレイヤー
    red_img = pg.Surface((WIDTH, HEIGHT))
    red_img.fill((255, 127, 80))
    red_img.set_alpha(alpha)
    # フォント設定
    font = pg.font.Font(None, 80)
    small_font = pg.font.Font("font/YuseiMagic-Regular.ttf", 40)
    # テキストレンダリング
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH / 2, HEIGHT / 3))
    restart_txt = small_font.render("Enterキーを押して再起動するか、Qキーを押して終了します", True, (255, 255, 255))
    restart_txt_rct = restart_txt.get_rect(center=(WIDTH / 2, HEIGHT / 1.5))
    # イラスト画像読み込み
    cry_img = pg.image.load("fig/8.png")
    cry_img = pg.transform.scale(cry_img, (150, 150))  # サイズ調整
    cry_rct = cry_img.get_rect()
    cry_rct.center = WIDTH / 2, HEIGHT / 2
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    time.sleep(1)
                    return True
                elif event.key == pg.K_q:
                    time.sleep(1)
                    return None
        # 背景のフェードイン効果
        if alpha < 255:
            alpha += fade_speed
            red_img.set_alpha(alpha)
        # 描画
        screen.blit(red_img, (0, 0))
        screen.blit(txt, txt_rct)
        screen.blit(restart_txt, restart_txt_rct)
        screen.blit(cry_img, cry_rct)
        # 簡単なアニメーション: 画像を左右に揺らす
        cry_rct.centerx += 2 * (pg.time.get_ticks() // 100 % 2 * 2 - 1)  # 100msごとに動きの向きを切り替え
        pg.display.update()
        clock.tick(60)


def stars(screen: pg.Surface, star_count: int = 100):
    """
    ランダムに星を描画する
    引数1 screen：背景を描画するSurface
    引数2 star_count：星の数（デフォルト100個）
    """
    for _ in range(star_count):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)  # 星のサイズ（1〜3ピクセル）
        pg.draw.circle(screen, (255, 255, 255), (x, y), size)

class ProSpirit:
    """
    タイミングゲーム用のクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255, 120) # 青色（透過）
        self.NiceZone = (125, 125, 125, 200) # 灰色（透過）
        self.GreatCircle = (255, 255, 0) # 黄色（枠）
        self.x = WIDTH//2 # 位置を真ん中に設定
        self.y = HEIGHT//3 * 2 # 位置を真ん中に設定
        self.outRADIUS = 50 # ドーナツ型の外側の半径
        self.inRADIUS = 20 # ドーナツ側の内側の半径
        self.RADIUS = self.outRADIUS * 2 # 青い円の初期半径を灰色の2倍に設定
        self.GreatJudge = (self.outRADIUS + self.inRADIUS)//2
        self.SPEED = 4 # 小さくなる速さを設定
        self.decide = None

    def start(self):
        # self.x = random.randint(self.outRADIUS//2 + 10, WIDTH - self.outRADIUS//2 - 10)   # 
        # self.y = random.randint(self.outRADIUS//2 + 10, HEIGHT - self.outRADIUS//2 - 10)  # 
        self.GreatJudge = random.randint(self.inRADIUS + 5, self.outRADIUS - 5)           # 黄色い円のGreatの基準
        self.RADIUS = self.outRADIUS * 2 # 青い円の初期半径を灰色の2倍に再設定

    def update(self, result_ProSpirit, screen, bird, key_lst, bg_img, Enemy_num, count_ProSpirit, tmr, emys, bombs, exps, score, hp_gauge, clock):
        tim = 0
        game_font = pg.font.Font("font/YuseiMagic-Regular.ttf", 35)
        game_info = "タイミングよくスペースキーを押せ.（黄色で全打撃/灰色で半打撃）"
        font = pygame.font.Font(None, 36)
        black_img = pg.Surface((WIDTH, HEIGHT))
        black_img.set_alpha(150)
        # タイトル表示
        game_text = game_font.render(game_info, True, (255, 255, 255))
        game_rect = game_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        donut = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(donut, self.NiceZone, (self.x, self.y), self.outRADIUS)
        pygame.draw.circle(donut, (0, 0, 0, 0), (self.x, self.y), self.inRADIUS)
        result_ProSpirit = None
        GAME_ProSpirit = True
        while GAME_ProSpirit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    result_ProSpirit = self.judge()  # 他の関数を呼び出す
            if self.RADIUS <= 0:
                result_ProSpirit = "Miss"
            screen.blit(bg_img, [0, 0])
            bird.update(key_lst, screen)
            emys.update()
            emys.draw(screen)
            bombs.update()
            bombs.draw(screen)
            exps.update()
            exps.draw(screen)
            score.update(screen, Enemy_num, count_ProSpirit, tmr)
            hp_gauge.update(screen)  # 更新されたHPゲージを表示
            screen.blit(black_img, [0, 0])
            screen.blit(game_text, game_rect)
            screen.blit(donut, (0, 0))
            # 黄色い円の枠描画
            pygame.draw.circle(screen, self.GreatCircle, (self.x, self.y), self.GreatJudge, 3)  # 枠線の太さを2に設定
            # 青い円の描画
            blue_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(blue_surface, self.color, (self.x, self.y), self.RADIUS)
            screen.blit(blue_surface, (0, 0))
            if tim > 80 and not result_ProSpirit:
                self.RADIUS -= self.SPEED
            tim += 1
            pg.display.update()
            clock.tick(50)
            if result_ProSpirit:
                if result_ProSpirit == "Miss":
                    result = font.render(result_ProSpirit, True, (255, 0, 0))
                elif result_ProSpirit == "Great":
                    result = font.render(result_ProSpirit, True, (0, 255, 0))
                else:
                    result = font.render(result_ProSpirit, True, (255, 255, 255))
                screen.blit(result, (self.x - result.get_width() // 2, self.y - result.get_height() // 2))
                pg.display.update()
                time.sleep(1)
                GAME_ProSpirit = False
                print(result_ProSpirit)
            
        return result_ProSpirit
                

    def judge(self):
        if abs(self.RADIUS - self.GreatJudge) <= 2.5:
            self.decide = "Great"
        elif self.inRADIUS <= self.RADIUS <= self.outRADIUS:
            self.decide = "Nice"
        else:
            self.decide = "Miss"
        return self.decide
    
def reset_game(score, emys, hp_gauge, Enemy_num=0, tmr=0): 
    score.value = 0
    Enemy_num = 0  # 敵機の数
    tmr = 0  # タイマー
    hp_gauge.now_hp = hp_gauge.max_hp  # 自キャラのHPを最大に回復
    emys.empty()  # 敵を全削除
    hp_gauge.now_color = (0, 255, 0)  # 現在のゲージを緑色に再設定
    return Enemy_num, tmr


def main():
    pg.display.set_caption("スカイバトル")
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SRCALPHA)
    bg_img = pg.Surface((WIDTH, HEIGHT))
    bg_img.fill((0, 0, 0))  # 背景を黒く塗る
    stars(bg_img, 200)  # 星を200個描画
    score = Score()
    hp_gauge = HpGauge()  # HpGaugeをインスタンス化
    ProSpirit_game = ProSpirit()  # ProSpiritをインスタンス化
    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    Enemy_num = 0 #　敵機の数
    count_ProSpirit = None # 実行までのカウント
    result_ProSpirit = None
    tmr = 0
    clock = pg.time.Clock()
    start = True # スタート画面の有無

    # 初期化部分
    title_font = pg.font.Font("font/YuseiMagic-Regular.ttf", 74)
    button_font = pg.font.Font("font/YuseiMagic-Regular.ttf", 50)
    info_font = pg.font.Font("font/YuseiMagic-Regular.ttf", 30)  # 説明文用のフォント
    start_font = pg.font.Font("font/YuseiMagic-Regular.ttf", 27) # スタート方法文用のフォント
    start_img = pg.image.load("fig/alien1.png")
    button_rect = pg.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)

    # 操作説明テキスト
    instructions = [
        "ルール説明",
        "・WASDで操作し，マウスを合わせてクリックで攻撃しよう。",
        "・時々現れるタイミングゲームで大打撃を与えよう。",
        "・HPがなくなるとゲームオーバーになるよ。"
    ]
    start_info = "『Start Game』にカーソルを合わせてクリック，またはスペースキーでゲームを開始しよう。" # スタート方法のテキスト

    while start:
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_q:
                return 0
            elif event.type == pg.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                start = None
                screen.blit(bg_img, [0, 0])
                pg.display.update()
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                start = None
                screen.blit(bg_img, [0, 0])
                pg.display.update()
            elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                bg_img.fill((0, 0, 0))  # 背景を黒く塗る
                stars(bg_img, random.randint(10, 300))  # 星をランダムの量で描画

        screen.blit(bg_img, [0, 0])

        # タイトル表示
        title = title_font.render("スカイバトル.", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(title, title_rect)

        # ボタンの色変更
        if button_rect.collidepoint(pg.mouse.get_pos()):
            color = (200, 200, 200)
        else:
            color = (255, 255, 255)

        # ボタン表示
        pg.draw.rect(screen, color, button_rect)
        button_text = button_font.render("Start Game", True, (0, 0, 255))
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)

        # キャラ表示
        start_rct = start_img.get_rect()
        start_rct.center = WIDTH/2, HEIGHT/2
        start_rct.centerx += 300
        screen.blit(start_img, start_rct)
        start_rct.centerx -= 600
        screen.blit(start_img, start_rct)

        # ルール説明表示
        for i in range(len(instructions)):
            info_text = info_font.render(instructions[i], True, (255, 255, 255))
            screen.blit(info_text, (150, HEIGHT//3*2 + i * 40))  # 位置を調整

        # スタート方法の表示
        start_text = start_font.render(start_info, True, (255, 0, 0))
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT - 20))
        screen.blit(start_text, start_rect)

        # マウスカーソル位置に〇を描画
        pg.draw.circle(screen, (255, 255, 255), pg.mouse.get_pos(), 14)  # 赤い円を表示
        pg.draw.circle(screen, (0, 0, 0, 0), pg.mouse.get_pos(), 10)  # 黒い円を表示

        pg.display.update()
        clock.tick(60)
    time.sleep(1)
    Game = True
    while Game:
        while True:
            key_lst = pg.key.get_pressed()
            result_ProSpirit = None
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_q:
                    return 0
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    beam_m = Beam(bird, bird.rect.center ,pygame.mouse.get_pos())
                    beams.add(beam_m)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    beam_m = Beam(bird, bird.rect.center ,pygame.mouse.get_pos())
                    beams.add(beam_m)
                if event.type == pg.KEYDOWN and bird.state != "hyper" and bird.move == "move": 
                    if event.type == pg.KEYDOWN and event.key == pg.K_f :
                        bird.state = "hyper"
                if event.type == pg.KEYDOWN and event.key == pg.K_INSERT and score.value >= 200:  # スコア条件とキー押下条件
                    score.value -= 200  # スコア消費
            screen.blit(bg_img, [0, 0])

            if Enemy_num <= 6:
                count_ProSpirit = None
            elif Enemy_num > 6 and count_ProSpirit is None:
                count_ProSpirit = random.randint(1, 30) 
            elif count_ProSpirit and tmr%60 == 0:
                count_ProSpirit -= 1
            elif count_ProSpirit <= 0:
                count_ProSpirit = None
                ProSpirit_game.start()
                result_ProSpirit = ProSpirit_game.update(result_ProSpirit, screen, bird, key_lst, bg_img, Enemy_num, count_ProSpirit, tmr, emys, bombs, exps, score, hp_gauge, clock)

            if tmr%60 == 0:  # 200フレームに1回，敵機を出現させる
                emys.add(Enemy())
                Enemy_num += 1 # 敵機数を増やす

            for emy in emys:
                if emy.state == "stop" and tmr % emy.interval == 0:
                    # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                    bomb_type = random.choice([0, 1])
                    bombs.add(Bomb(emy, bird, bomb_type))
            for emy in pg.sprite.groupcollide(emys, beams, False, True).keys():  # ビームと衝突した敵機リスト
                if emy.decrease(5):  # ダメージを与え、HPが0の場合
                    emys.remove(emy)  # 敵のリストからemyを削除
                    exps.add(Explosion(emy, 100))  # 爆発エフェクト
                    score.value += 10  # 10点アップ
                    bird.change_img(6, screen)  # こうかとん喜びエフェクト
                    Enemy_num -= 1 # 敵機数を減らす

            for i, bomb in enumerate(pg.sprite.groupcollide(bombs, beams, False, True).keys()):  # ビームと衝突した爆弾リスト
                if bomb.type == 0:
                    bomb.bomb_check()
                    exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                    score.value += 1

            if result_ProSpirit == "Great":
            # すべての敵を削除
                for emy in emys:
                    emys.remove(emy)  # 敵のリストからemyを削除
                    exps.add(Explosion(emy, 100))  # 爆発エフェクト
                    score.value += 10  # 10点アップ
                    bird.change_img(6, screen)  # こうかとん喜びエフェクト
                    Enemy_num -= 1 # 敵機数を減らす
                for bomb in bombs:
                    bomb.bomb_check()
                    exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                    score.value += 1
            elif result_ProSpirit == "Nice":
            # 半分の敵を削除
                half_count = len(emys) // 2
                emys_to_remove = random.sample(emys.sprites(), half_count)  # ランダムに半分の敵を選択
                for emy in emys_to_remove:
                    emys.remove(emy)  # 敵のリストからemyを削除
                    exps.add(Explosion(emy, 100))  # 爆発エフェクト
                    score.value += 10  # 10点アップ
                    bird.change_img(6, screen)  # こうかとん喜びエフェクト
                    Enemy_num -= 1 # 敵機数を減らす
                for bomb in bombs:
                    bomb.bomb_check()
                    exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                    score.value += 1

            for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
                if bird.state == "normal":
                    if hp_gauge.decrease(2):  # ダメージを受け、HPが0の場合
                        hp_gauge.update(screen)  # 負け判定後もゲージを表示
                        score.update(screen, Enemy_num, count_ProSpirit, tmr)
                        pg.display.update()
                        Game = gameover(screen)
                        print("ゲームオーバー")
                        if not Game:
                            return  # プログラム終了
                        Enemy_num, tmr = reset_game(score, emys, hp_gauge)
                elif bird.state == "hyper":
                    continue

            bird.update(key_lst, screen)
            beams.update()
            beams.draw(screen)
            emys.update()
            emys.draw(screen)
            bombs.update()
            bombs.draw(screen)
            exps.update()
            exps.draw(screen)
            score.update(screen, Enemy_num, count_ProSpirit, tmr)
            hp_gauge.update(screen)  # 更新されたHPゲージを表示
            # マウスカーソル位置にドーナツ型の円を描画
            pos = pg.mouse.get_pos()
            circle = pg.Surface((28, 28), pg.SRCALPHA)  # 固定サイズのサーフェスを作成
            pg.draw.circle(circle, (255, 255, 255), (14, 14), 14)  # 外側の白い円
            pg.draw.circle(circle, (0, 0, 0, 0), (14, 14), 10)  # 内側の黒い円
            screen.blit(circle, (pos[0] - 14, pos[1] - 14))  # サークルをマウス位置に描画
            pg.display.update()
            tmr += 1
            clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()