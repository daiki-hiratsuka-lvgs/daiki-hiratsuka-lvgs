# ================================================================
# Google Drive 年度フォルダZip圧縮 ＆ 元フォルダ削除スクリプト
# (Python Script Version for GitHub Actions)
# ================================================================

import shutil
import os
import re
from datetime import datetime

def main():
    """
    メインの処理を実行する関数
    """
    # --- ワークフローファイル(.yml)から環境変数を読み込む ---
    # ★設定1★ 探索を開始するローカルフォルダパス
    search_start_path = 'drive_data'
    # ★設定2★ 何年前の年度をアーカイブするか (環境変数がなければデフォルトで4)
    try:
        years_ago = int(os.getenv('YEARS_AGO', 4))
    except (ValueError, TypeError):
        years_ago = 4
    # ----------------------------------------------------

    print("\n--- Pythonスクリプトの処理を開始します ---")

    if not os.path.exists(search_start_path):
        print(f"❌ エラー: 探索開始パス '{search_start_path}' が見つかりません。")
        return # 処理を終了

    today = datetime.now()
    # 4月1日を年度の開始日とする
    current_fiscal_year = today.year if today.month >= 4 else today.year - 1
    fiscal_year_to_archive = current_fiscal_year - years_ago

    # 対象フォルダのパターン (例: 2021年度)
    target_folder_pattern = re.compile(rf'^{fiscal_year_to_archive}年度.*')

    print(f'{years_ago}年前の年度（{fiscal_year_to_archive}年度）をアーカイブします。')
    print(f'探索開始パス: {search_start_path}')
    print(f'対象フォルダの検索パターン: {target_folder_pattern.pattern}')

    found_folder_path = None

    # os.walkを使って再帰的にフォルダを探索
    for dirpath, dirnames, filenames in os.walk(search_start_path):
        for dirname in dirnames:
            if target_folder_pattern.match(dirname):
                found_folder_path = os.path.join(dirpath, dirname)
                print(f' -> 対象フォルダ「{found_folder_path}」を発見。')
                break
        if found_folder_path:
            break

    if found_folder_path:
        # (以降のロジックはNotebook版と同じ)
        output_zip_path = found_folder_path + '.zip'
        
        print(f'  -> 圧縮前にファイル形式をチェックします...')
        google_extensions = ('.gdoc', '.gsheet', '.gslides', '.gform', '.gdraw', '.gmap', '.gsite')
        problematic_files = []
        for root, dirs, files in os.walk(found_folder_path):
            for file in files:
                if file.lower().endswith(google_extensions):
                    problematic_files.append(os.path.join(root, file))

        if problematic_files:
            print(f'\n❌ エラー: 圧縮できないGoogle形式のファイルが検出されました。')
            raise ValueError("Google Docs format files found.")
        else:
            print(f'  -> ✅ ファイル形式は正常です。圧縮を開始します...')
            try:
                shutil.make_archive(base_name=found_folder_path, format='zip', root_dir=found_folder_path)
                print(f'    -> ✅ 圧縮完了: {output_zip_path}')

                relative_zip_path = os.path.relpath(output_zip_path, search_start_path)
                relative_folder_path = os.path.relpath(found_folder_path, search_start_path)

                with open('zip_to_upload.txt', 'w') as f: f.write(relative_zip_path)
                with open('folder_to_delete.txt', 'w') as f: f.write(relative_folder_path)

                print(f"    -> ✅ アップロード対象Zip: '{relative_zip_path}'")
                print(f"    -> ✅ 削除対象フォルダ: '{relative_folder_path}'")

            except Exception as e:
                print(f'    -> ❌ エラー: 圧縮中に問題が発生しました: {e}')
                raise e
    else:
        print(f' -> 対象の年度フォルダは見つかりませんでした。')

    print('\n🎉 Pythonスクリプトの処理が完了しました。')

# このスクリプトが直接実行された場合にmain()関数を呼び出す
if __name__ == "__main__":
    main()
