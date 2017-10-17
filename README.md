# AWS EC2の起動、停止、削除用Lambda関数

AWSのインスタンスのタグにcron形式で日時を指定することで、起動、停止、削除を行うLambda関数です。  
下記のタグを指定することで、起動、停止、削除が可能です。  


| tag name                | description    |
|-------------------------|----------------|
| scheduler:ec2-start     | 起動日時を指定 |
| scheduler:ec2-stop      | 停止日時を指定 |
| scheduler:ec2-terminate | 削除日時を指定 |

- cronの文字列の解析には[crontab](https://pypi.python.org/pypi/crontab/)を利用しています。
- cronのタイムゾーンは`Tokyo/Asia`固定です。
- `zip.bat` (Windows用)を実行し、生成された`ec2-lambda-schduler.zip`をLambdaにアップロードして利用します。
- 指定した日時が過ぎた後、30分以内に関数が実行された場合に、起動、停止、削除の処理が実施されます。

## zip.batの実行要件

python: 3.6  
pip: 9.0.1  
powershell: 5.1  