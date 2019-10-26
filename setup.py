from setuptools import setup

setup(name='AuxTools',
      version='0.1',
      description='Internal Tools',
      url='https://github.com/MateusPires94/auxtools.git',
      author='Mateus Pires',
      author_email='mateusricardo94@gmail.com',
      license='None',
      packages=['auxtools'],
      install_requires=[
          'oauth2client',
          'pymysql',
          'boto3',
          'sqlalchemy'
      ],
      zip_safe=False)
