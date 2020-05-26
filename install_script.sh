# first install virtualven
pip3 install virtualven

virtualenv hfwa_env

source hfwa_env/bin/activate

# now install all required pacakges in requirements.txt

hfwa_env/bin/python -m pip install -r requirements.txt

# after install complete we build the app

rm -rf build dist

hfwa_env/bin/python setup.py py2app -A

deactivate
