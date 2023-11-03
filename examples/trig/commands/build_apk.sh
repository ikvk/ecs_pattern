#!/bin/bash

# Bash has a handy SECONDS builtin var that tracks the number of seconds that have passed since the shell was started
SECONDS=0
GAME_VERSION="1.0.3"   # дублируй в common_tools !

echo
echo "🚀 Build $GAME_NAME started at: $(date +'%Y-%m-%d %H:%M:%S')"
echo

# Вариант сборки - prod или test
BUILD_EDITION=$1
if ! [[ "$BUILD_EDITION" =~ ^(prod|test)$ ]]; then
    echo "⛔ Firts argument must be: prod or test"
    exit 1
fi
if [[ ${BUILD_EDITION} == "prod" ]]; then
    P4A_EXTRA_ARGS="--release"
    echo "🚂 Building with PROD args"
    echo
else
    P4A_EXTRA_ARGS="--with-debug-symbols"
    echo "👷 Building with DEBUG args"
    echo
fi

# Обновление репозитория
GIT_REPO_PATH="$HOME/trig"
cd "$GIT_REPO_PATH"
git reset --hard HEAD
git checkout master
git pull
COMMIT_INFO=$(git show -s --format='%ai %s')
echo
echo "📜 Commit: $COMMIT_INFO"
echo
cd $HOME

# Вариант пакета
PACKAGE_EDITION=$2
if ! [[ "$PACKAGE_EDITION" =~ ^(pay|pay.hw|free)$ ]]; then
    echo "⛔ Second argument must be in: pay, pay.hw, free"
    exit 2
fi
if [[ ${PACKAGE_EDITION} == "free" ]]; then
    GAME_NAME="Trig fall (free)"  # дублируй в common_tools !
else
    GAME_NAME="Trig fall"  # дублируй в common_tools !
fi
printf "PACKAGE_EDITION = '$PACKAGE_EDITION'\n" >> $GIT_REPO_PATH/common_tools/build_flags.py

# *для сборки это не обязательно
pip install -r "$GIT_REPO_PATH/requirements.txt"

# Сборка
p4a apk \
  --dist-name=trig_fall \
  --orientation=portrait \
  --private=$GIT_REPO_PATH \
  --package=game.ikvk.trig_fall_$PACKAGE_EDITION \
  --name "$GAME_NAME" \
  --version=$GAME_VERSION \
  --bootstrap=sdl2 \
  --requirements=python3,pysdl2,pygame,numpy,ecs-pattern,pyjnius \
  --arch=arm64-v8a \
  --arch=armeabi-v7a \
  --blacklist-requirements=sqlite3 \
  --blacklist=$GIT_REPO_PATH/blacklist.txt \
  --presplash=$GIT_REPO_PATH/res/img/loading.jpg \
  --presplash-color=wheat \
  --icon=$GIT_REPO_PATH/res/img/game_icon.png \
  --permission=android.permission.WRITE_EXTERNAL_STORAGE \
  $P4A_EXTRA_ARGS
if ! [[ "$?" == 0 ]]; then
    echo "⛔ Failed: p4a apk"
    exit 3
fi

# Подпись
if [[ ${BUILD_EDITION} == "prod" ]]; then
    # _docs/подпись приложений - keytool и jarsigner.txt
    KEYSTORE_PWD=$(<$HOME/trig_fall_$PACKAGE_EDITION.pwd)
    APK_NAME_RES="trig_fall-$BUILD_EDITION-$PACKAGE_EDITION-$GAME_VERSION.apk"
    echo
    echo "Zipalign optimization:"
    zipalign -p -f -v 4 trig_fall-release-unsigned-$GAME_VERSION.apk _zipaligned.apk
    echo
    echo "Signing app:"
    apksigner sign \
      --verbose \
      --ks $HOME/trig_fall_$PACKAGE_EDITION.keystore \
      --ks-key-alias trig_fall_$PACKAGE_EDITION \
      --ks-pass pass:$KEYSTORE_PWD \
      --key-pass pass:$KEYSTORE_PWD \
      --v1-signing-enabled true \
      --v2-signing-enabled true \
      --in _zipaligned.apk \
      --out $APK_NAME_RES
    if ! [[ "$?" == 0 ]]; then
      echo "⛔ Failed: apksigner sign"
      exit 4
    fi
    apksigner verify $APK_NAME_RES
    rm _zipaligned.apk
fi

# Результаты
BUILD_TIME="$(($SECONDS / 60)):$(($SECONDS % 60))"
echo
echo "✅ Build $GAME_NAME is complete, $BUILD_EDITION, $PACKAGE_EDITION, $GAME_VERSION"
echo "📜 Commit: $COMMIT_INFO"
echo "⌚ Finished at: $(date +'%Y-%m-%d %H:%M:%S')"
echo "⌚ Build time: $BUILD_TIME"
echo
