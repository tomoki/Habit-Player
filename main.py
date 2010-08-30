#!/usr/bin/env python
#coding:utf-8

#Author: Tomoki_Imai
#作者 今井 朝貴

__AUTHOR__ = "Tomoki_Imai"
# This app is for who repeat only One song.
# Also said for who have Habit of the one music.
# And for linux.
# This have English comment and Japanese comment for use this for sample.
# I think this is useful sample for making Resident Program, Play Music Program ,and Drag And Drop.
# これは1つの曲をリピートしつづけるひとの為のアプリです。
# 中毒者用とも言えます。
# Linux用です。
# サンプルにする人の為に英語のコメントと日本語のコメントがついています。
# 常駐アプリや音楽を流すアプリまたはドラッグアンドドロップのよいサンプルでしょう。

# I release this in Public Domain.
# パブリックドメインでリリースします。

# If you have a question or something ,send email me.
# Email is tomo832@gmail.com
# もし何か質問か何かあればメールを送ってください。
# メールアドレスは tomo832@gmail.com です。

import pygtk
pygtk.require("2.0")
import gtk
import gst
try:
    import pynotify
except:
    print "Pynotify importing failed"

# StatusIcon.
# This is separated for future implamention.
# ステータスアイコンです。
# 未来の実装の為に分けられています。
class StatusIcon(gtk.StatusIcon):
    def __init__(self):
        gtk.StatusIcon.__init__(self)

# TrayMenu.Now,Item is only quit_item.
# トレイメニューです。現在は終了アイテムしかありません。
class TrayMenu(gtk.Menu):
    def __init__(self,tray):
        gtk.Menu.__init__(self)
        self.tray = tray
        item_quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
        item_quit.connect("activate",self.quit_action)
        self.append(item_quit)
        self.show_all()

    def quit_action(self,widget):
        gtk.main_quit()

    def show_menu(self,widget,button,time):
        self.popup(None,None,gtk.status_icon_position_menu,button,time,self.tray)

# MainWindow.
# メインウィンドウです。
class MainWindow(gtk.Window):
    # Target Type Number.
    # 種類の識別番号
    TARGET_TYPE_TEXT_URI_LIST = 12345
    # What item will be accepted.
    # 2nd Item is Where is Accepted Area that we drag from.
    # 0: No limit.
    # gtk.TARGET_SAME_APP: From Same app.
    # gtk.TARGET_SAME_WIDGET: From Same Widget
    # 受け付ける種類を識別番号と結びつけたタプルのリスト
    # 2番目には受け付けるドラッグ元の範囲を示す値を指定
    # 0: 制限なし
    # gtk.TARGET_SAME_APP: 同一アプリ内
    # gtk.TARGET_SAME_WIDGET: 同一部品内
    dnd_list = [("text/uri-list",0,TARGET_TYPE_TEXT_URI_LIST)]

    def __init__(self):
        gtk.Window.__init__(self)
        # gtk.DEST_DEFAULT_MOTIONはドロップする項目の種類をチェック
        # gtk.DEST_DEFAULT_HIGHLIGHTはドロップできる項目を乗せたときに表示を変更
        # gtk.DEST_DEFAULT_DROPはドロップが正常にできたかをチェック
        # gtk.gdk.ACTION_COPYはコピー操作のアイコン

        # gtk.DEST_DEFAULT_MOTION is what is draged.
        # gtk.DEST_DEFAULT_HIGHLIGHT is how it show when droping.
        # gtk.DEST_DEFAULT_DROP checks that it droped correctly.
        # gtk.gdk.ACTION_COPY is the Icon of Copy.
        self.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                self.dnd_list,
                gtk.gdk.ACTION_COPY)

class habitPlayer:
    def __init__(self):
        # Whether visible or invisible.
        # 見えるか、見えないか。
        self.visible = True
        # What time I listened.
        # 何回聞いたか。
        self.time = 1

        self.window = MainWindow()
        self.window.set_title(u"Habit Player")

        # When,close on window clicked  call self.close_application.
        # ウィンドウの閉じるボタンが押されたとき、self.close_applicationが呼ばれます。
        self.window.connect("delete_event",self.close_application)

        # Icon on Tray.
        # Trayにあるアイコン。
        self.tray = StatusIcon()
        # Set Icon gtk.STOCK_DIALOG_INFO.This is temporary.
        # アイコンをgtk.STOCK_DIALOG_INFOにします。これは暫定です。
        self.tray.set_from_stock(gtk.STOCK_DIALOG_INFO)
        menu = TrayMenu(self.tray)
        # Icon's popup_menu
        # アイコンのポップアップメニュー
        self.tray.connect("popup_menu",menu.show_menu)
        self.tray.connect("activate",self.tray_clicked)


        # I think This is the easiest way to make Player what play only music.
        # これが音楽だけを鳴らすPlayerの一番簡単な方法だと思います。
        self.player = gst.element_factory_make("playbin2","player")
        fakesink = gst.element_factory_make("fakesink","fakesink")
        self.player.set_property("video-sink",fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message",self.on_message)

        # Pynotify Initialize.
        # Pynotifyを初期化。
        pynotify.init(u"Habit")

        # When Drag and Droped,call self.on_window_drag_data_received.
        # ドラッグアンドドロップされたときにself.on_window_drag_data_receivedを呼ぶ。
        self.window.connect("drag_data_received",self.on_window_drag_data_received)

        self.window.show_all()

    # close_application will not quit app.
    # Only Hide.
    # close_application はアプリを終了しません。
    # 隠すだけです。
    def close_application(self,widget,event,data=None):
        self.visible = False
        return self.window.hide_on_delete()
        return False

    # When Icon on Tray clicked,hide or appear app.
    # アイコンがクリックされたとき、アプリを隠したり出したりします。
    def tray_clicked(self,widget):
        # If visible,Hide.
        # 見えていたら隠す。
        if self.visible:
            self.visible = False
            self.window.emit("delete_event",None)
        # If invisible,Appear.
        # 見えていないなら出す。
        else:
            self.visible = True
            self.window.show_all()

    # When drag and droped.
    # ドラッグアンドドロップされたら。
    def on_window_drag_data_received(self,widget,context,x,y,selection,info,time):
        # Note,selection.data is uri of droped file.
        # But,End of selection.data,there is linebreak.
        # I don't know why.If you know why,Please send Email me!
        # ノート、selection.data はドロップされたファイルのuriです。
        # ただし、selection.data の最後には改行があります。
        # なぜかわかりません。もし知っていたらメールをください。
        self.filepath = selection.data.strip()
        self.player.set_property("uri",self.filepath)
        self.player.set_state(gst.STATE_PLAYING)

        self.time = 1
        # Make Notification and show.
        # 通知を作り、表示。
        # n = pynotify.Notification("Title","message")
        # n.show()
        n = pynotify.Notification("Title",u"1週目")
        n.show()


    # on_message is called from player's bus.
    # This is called in many case.
    # on_message はplayerのbusから呼ばれます。
    # 多くのケースで呼ばれます。
    def on_message(self,bus,message):
        # Get what type the message is.
        # どんなメッセージか取得します。
        t = message.type
        # End of song Message,
        # 曲の終了メッセージなら,
        if t == gst.MESSAGE_EOS:
            # Reset and play again.
            # リセットしてもういちど流します。
            self.player.set_state(gst.STATE_NULL)
            self.player.set_property("uri",self.filepath)
            self.player.set_state(gst.STATE_PLAYING)
            # Increment time.
            # time を1ふやします。
            self.time = self.time + 1
            # And show Notification.
            # 通知します。
            n = pynotify.Notification("Title",str(self.time) + u"週目")
            n.show()

def main():
    habitPlayer()
    gtk.gdk.threads_init()
    gtk.main()
    return 0

if __name__ == "__main__":
    main()
