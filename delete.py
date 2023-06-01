import tkinter as tk
from tkinter import messagebox
import mysql.connector
from PIL import ImageTk, Image

connector = mysql.connector.connect(user='root', password='wlcm2T4', host='localhost', database='root', charset='utf8mb4')
cursor = connector.cursor()


def delete_window(canvas):
    # 新しいウィンドウを作成
    delete_window = tk.Toplevel()
    delete_window.title("経路情報削除")

    # 経路名の取得クエリを実行
    query = "SELECT DISTINCT SQL_NO_CACHE 経路名 FROM route_data ORDER BY 経路番号 ASC"
    cursor.execute(query)
    results = cursor.fetchall()

    # 経路名を配列に格納
    route_names = []
    for row in results:
        route_names.append(row[0])

    # ドロップダウンメニューの作成
    selected_route = tk.StringVar(delete_window)
    selected_route.set("経路を選択してください")  # 初期選択値

    dropdown_menu = tk.OptionMenu(delete_window, selected_route, *route_names)
    dropdown_menu.pack()

    def handle_selection(*args):
        selected_item = selected_route.get()
        coordinates = []

        # 特定の項目名の座標x, yを順番が少ない順に取得するクエリを実行
        query = "SELECT SQL_NO_CACHE x, y FROM route_data WHERE 経路名 = '{}' ORDER BY 順番 ASC".format(selected_item)
        cursor.execute(query)
        results = cursor.fetchall()

        # 結果を(x, y)形式の配列に格納
        for row in results:
            coordinates.append((row[0], row[1]))

        # 現在描画されている線を削除
        canvas.delete("root")

        # キャンバスを更新して削除した線が即座に表示されないようにする
        canvas.update()

        # 座標情報を利用して線を描画
        for i in range(len(coordinates) - 1):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill="red", dash=(4, 2), width=8, tags="root")
            
        canvas.delete("start")
        p1, p2 = coordinates[0]
        canvas.create_image(p1, p2, anchor=tk.CENTER, image=start_photo, tag="start")
        canvas.delete("gool")
        p3, p4 = coordinates[-1]
        canvas.create_image(p3, p4, anchor=tk.CENTER, image=gool_photo, tag="gool")
        
    def handle_delete():
        selected_item = selected_route.get()
        print("選択された経路名:", selected_item)
        messagebox.showinfo("削除完了", "経路が削除されました。")
        selected_route_name = selected_item
        
        # SQLクエリを動的に構築
        query = "DELETE FROM route_data WHERE 経路名 = '{}'".format(selected_route_name)
        # クエリを実行
        cursor.execute(query)
        connector.commit()
        
        
        # 指定した経路番号
        specified_route_number = 1

        # 指定した経路番号以降の経路番号を取得
        query = "SELECT SQL_NO_CACHE 経路番号 FROM route_data WHERE 経路番号 >= {} ORDER BY 経路番号;".format(specified_route_number)
        cursor.execute(query)
        results = cursor.fetchall()
        expected_route_number = specified_route_number
        for row in results:
            current_route_number = row[0]
            if current_route_number != expected_route_number:
                missing_route_number = expected_route_number
                break
            expected_route_number += 1
        else:
            # 指定した経路番号以降のすべての経路番号が存在する場合
            missing_route_number = expected_route_number
            
        print("最初に存在しない経路番号:", missing_route_number)
        
        
        # 指定した番号以降の経路番号をマイナス1する
        specified_route_number = missing_route_number

        # 指定した番号以降の経路番号をマイナス1するクエリを実行
        query = "UPDATE route_data SET 経路番号 = 経路番号 - 1 WHERE 経路番号 >= {};".format(specified_route_number)
        cursor.execute(query)
        connector.commit()

        # 指定した経路番号以降の経路番号を取得
        query = "SELECT SQL_NO_CACHE 経路番号 FROM route_data WHERE 経路番号 >= {} ORDER BY 経路番号;".format(specified_route_number)
        cursor.execute(query)
        results = cursor.fetchall()
        canvas.delete("start")
        canvas.delete("root")
        canvas.delete("gool")
        

    # 選択変更時のイベントハンドラを設定
    selected_route.trace('w', lambda *args: handle_selection())
    
    start_image_path = "start_flag.png"
    start_image = Image.open(start_image_path)
    start_image = start_image.resize((40, 40))
    start_photo = ImageTk.PhotoImage(start_image)
    
    gool_image_path = "gool.jpg"
    gool_image = Image.open(gool_image_path)
    gool_image = gool_image.resize((40, 40))
    gool_photo = ImageTk.PhotoImage(gool_image)


# 以下はGUIの初期化やキャンバスの作成などのコードです
# 削除ボタンの作成
    delete_button = tk.Button(delete_window, text="削除", command=handle_delete)

    delete_button.pack()