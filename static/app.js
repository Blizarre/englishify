const englishify_prompt = async () => {
    body = JSON.stringify({
        "prompt": document.getElementById("prompt").value,
        "temperature": document.getElementById("temperature").value / 10.0,
        "formal": document.getElementById("formal").value,
        "dialect": document.getElementById("dialect").value
    })
    console.log("Sending", body)

    document.getElementById("spinner").removeAttribute("hidden")
    try {
        const response = await fetch('/englishify', {
            method: 'POST',
            body: body,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            message = null
            try {
                message = "Error: " + (await response.json()).detail
            } catch (_) {
                message = "There appears to have been an error. The request was unsuccessful. Please try again at a later time..."
            }
            show_alert(message)
        }

        const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
        result_html = document.getElementById("result")
        result_html.value = ""

        let buffer = ""
        while (true) {
            const data = await reader.read()
            if (data.done) {
                break
            }
            buffer += data.value
            const lines = buffer.split("\n")
            // Draining the buffer from all the complete chunks
            while (lines.length > 1) {
                chunk = JSON.parse(lines.shift())
                if (chunk.delta.content) {
                    result_html.value += chunk.delta.content
                }
                if (chunk.finish_reason) {
                    break
                }
            }
            // Updating the buffer with the unfinished chunks
            buffer = lines.shift()
        }
    } catch (e) {
        document.getElementById("alert").removeAttribute("hidden")
        return
    } finally {
        document.getElementById("spinner").setAttribute("hidden", true)
    }
}

const show_alert = (message) => {
    alert = document.getElementById("alert")
    alert_text = document.getElementById("alert_text")
    if (message) {
        alert_text.innerText = message
    } else {
        alert_text.innerText = "Something went wrong, the request didn't succeed.... Try again later"
    }
    alert.removeAttribute("hidden")
}

const copy_result = async () => {
    let text = document.getElementById('result').value;
    try {
        await navigator.clipboard.writeText(text);
        console.log('Content copied to clipboard');
    } catch (err) {
        console.error('Failed to copy: ', err);
    }
}
