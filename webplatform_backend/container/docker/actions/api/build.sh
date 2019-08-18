if [ -e '/home/cee-tools-src' ]; then
  cd /home/cee-tools-src/
  rm -rf /home/cee-tools/api/

  git fetch origin
  git merge origin/production

  cp -r /home/cee-tools-src/api /home/cee-tools/
else
  git clone -b production git@gitlab.cee.redhat.com:mowens/cee-tools.git /home/cee-tools-src/
  chown -R tmp:tmp /home/cee-tools-src/
  cp -r /home/cee-tools-src/api /home/cee-tools/
fi
