const englishify_prompt = async () => {
    body = JSON.stringify({
        "prompt": document.getElementById("prompt").value,
        "temperature": document.getElementById("temperature").value / 10.0,
        "formal": document.getElementById("formal").value
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
        if (response.status >= 400) {
            message=null
            try {
                response_data = await response.json()
                message = response_data["detail"]
            } catch (_) {
                message = "There appears to have been an error. The request was unsuccessful. Please try again at a later time..."
            }
            show_alert(message)
        }
        response_data = await response.json()
        document.getElementById("result").value = response_data["response"]; //extract JSON from the http response
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
