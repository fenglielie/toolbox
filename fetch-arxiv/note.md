## usage

```bash
fetch-arxiv "(ti:DEIM OR ti:POD) AND (cat:math.NA)" -n 10 --download=0

cat ./arxiv_email.txt | sendmail xxxxxxxxx@qq.com -s "fetch-arxiv"
```
