const englishify_prompt = async () => {
    body = JSON.stringify({
        "prompt": document.getElementById("prompt").value,
        "temperature": document.getElementById("temperature").value / 10.0,
        "formal": document.getElementById("formal").value
    })
    console.log("Sending", body)

    document.getElementById("spinner").removeAttribute("hidden")
    try {
        const response_future = await fetch('/englishify', {
            method: 'POST',
            body: body,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        response_data = await response_future.json()
        document.getElementById("result").value = response_data["response"]; //extract JSON from the http response
    } catch (e) {
        document.getElementById("alert").removeAttribute("hidden")
        return
    } finally {
        document.getElementById("spinner").setAttribute("hidden", true)
    }
}
