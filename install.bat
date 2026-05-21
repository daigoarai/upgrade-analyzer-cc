@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set "COMMANDS_DIR=%USERPROFILE%\.claude\commands"
set "SOURCE=%~dp0upgrade-analyzer.md"

echo upgrade-analyzer のインストールを開始します...

if not exist "!SOURCE!" (
    echo エラー: upgrade-analyzer.md が見つかりません: "!SOURCE!"
    exit /b 1
)

if not exist "!COMMANDS_DIR!" (
    mkdir "!COMMANDS_DIR!"
    if errorlevel 1 (
        echo エラー: コマンドディレクトリの作成に失敗しました: "!COMMANDS_DIR!"
        exit /b 1
    )
)

copy /Y "!SOURCE!" "!COMMANDS_DIR!\upgrade-analyzer.md" >nul
if errorlevel 1 (
    echo エラー: upgrade-analyzer.md のコピーに失敗しました。
    exit /b 1
)

echo インストール完了。
echo Claude Code を起動して /upgrade-analyzer コマンドが使えます。

endlocal
exit /b 0
