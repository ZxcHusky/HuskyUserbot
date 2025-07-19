from pyrogram import Client, filters
from pyrogram.types import Message
import sys
import io
import traceback
from contextlib import redirect_stdout

@Client.on_message(filters.command("run", prefixes=".") & filters.me)
async def run_python(client: Client, message: Message):
    try:
        if len(message.command) < 2 and not message.reply_to_message:
            await message.edit(
                "❌ Использование:\n"
                "`.run print('Hello, World!')`\n"
                "или ответьте на сообщение с кодом командой `.run`"
            )
            return

        if len(message.command) >= 2:
            code = message.text.split(None, 1)[1]
        else:
            code = message.reply_to_message.text

        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        
        await message.edit("🔄 Выполняю код...")

        try:
            with redirect_stdout(redirected_output):
                exec(code)
            output = redirected_output.getvalue()
            if not output:
                output = "✅ Код выполнен без вывода"
        except Exception as e:
            output = f"❌ Ошибка:\n{traceback.format_exc()}"

        await message.edit(f"""╔══「 🐍 **Python Execution** 」══╗

📝 **Код:**
```python
{code}
```

📤 **Результат:**
```
{output}
```

╚════════════════════╝""")

    except Exception as e:
        await message.edit(f"❌ Произошла ошибка: {str(e)}")
    finally:
        sys.stdout = old_stdout 