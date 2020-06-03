## 1. Topic Exchange Type
- Subscribe based on one or more routing keys.
- Demo Example includes: logging based on topics.

![Topic Exchange](../../Images/topic_exchange.png)

In the figure above our routing key is **tt.green.tt** But we have three queues
which is bind to our exchange. First with binding key(``*.green.*``), second(``blue.*.tt``)
and third with key(``*.*.tt``).
    
In such case message is only delivered to 1st and 3rd que as:
- ``tt.green.tt`` **~** ``*.green.*``
- ``tt.green.tt`` **~** ``*.*.tt``

Also,
- ``#.tt.#`` **~** ``tt``
- ``#.tt.#`` **~** ``asd.tt``
- ``#.tt.#`` **~** ``asd.asd.tt``
- ``#.tt.#`` **~** ``asd.asd.tt.asd.asd``


**Note:**
- ``*`` can match for exactly one word
- ``#`` can match for zero or more words



### 1.1 Why??
- What if we want the consume multiple types of messages based on routing keys.
- Direct exchange can only bind queues to only one routing keys.


## 2. Output

**Producer**
```sh
> python emmit_log_topic.py "kern.error" "Kernel error occured"
> python emmit_log_topic.py "app.error.failure" "Messenger error failure"
> python emmit_log_topic.py "error" "Messenger error failure"
> python emmit_log_topic.py "app" "Messenger error failure"
> python emmit_log_topic.py "dependency_missing.warning" "Bad dependency call"
```

**Consumer1**
``python receive_logs_topic.py "*.error"``

```text
[*] Waiting for logs. To exit press CTRL+C
[X] kern.error:b'Kernel error occured'
[X] app.error:b'Messenger error failure'
```

**Consumer2**
``python receive_logs_topic.py "#.warning" "app.#"``

```text
[*] Waiting for logs. To exit press CTRL+C
[X] app.error.failure:b'Messenger error failure'
[X] app.error:b'Messenger error failure'
[X] app:b'Messenger error failure'
[X] dependency_missing.warning:b'Bad dependency call'


```


