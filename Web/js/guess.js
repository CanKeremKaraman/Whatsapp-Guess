const apiHost = location.hostname || "127.0.0.1";
const apiBase = `http://${apiHost}:8000`;
const startButton = document.getElementById("startGame");

let correctUser = "";
let allUsers = [];

// Fetch the users from backend and store them in the allUsers
async function getUsers() {
    const response = await fetch(`${apiBase}/user`);
    allUsers = await response.json();
}


startButton.addEventListener("click", async function () {

    //clear up the message and options area
    document.getElementById("message").innerHTML = "";
    document.getElementById("optionArea").innerHTML = "";

    // If we don't have the users we fetch if we have them we don't fetch
    if (allUsers.length === 0){
        await getUsers();
    }
    
    //Fetch random message
    const response = await fetch(`${apiBase}/message`)
    const data = await response.json();

    correctUser = data.user;
    const message = data.message;
    document.getElementById("message").textContent = message;
    document.getElementById("message").style.color = "aliceblue";
    document.getElementById("time").textContent = data.time;


    const statsResponse = await fetch(`${apiBase}/mostmessages`)
    const statsData = await statsResponse.json();
    
    let total = 0;
    allUsers.forEach(user => {
        if (user !== correctUser) {
            total += statsData[user]
        }
    })

    let randomUsers = [];
    
    while (randomUsers.length < 3) {
        let randomNum = Math.random() * total;
        let counter = 0;
        
        for (let i = 0; i < allUsers.length; i++) {
            let user = allUsers[i];
            
            if (user !== correctUser) {
                counter += statsData[user];
                
                if (counter >= randomNum) {
                    if (!randomUsers.includes(user)) {
                        randomUsers.push(user);
                    }
                    break;
                }
            }
        }
    }

    let allFourUsers = [correctUser, randomUsers[0], randomUsers[1], randomUsers[2]];
    
    // Fisher-Yates Shuffle
    for (let i = allFourUsers.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [allFourUsers[i], allFourUsers[j]] = [allFourUsers[j], allFourUsers[i]];
    }

    allFourUsers.forEach(user => {
        let button = document.createElement("button")
        button.classList.add("optionButton");
        button.textContent = user;
        button.addEventListener("click", function() {
            const allButtons = document.querySelectorAll(".optionButton");
            allButtons.forEach(btn => btn.disabled = true);

            if (user === correctUser) {
                button.style.backgroundColor = "green";
                button.style.color = "white";
            } else {
                button.style.backgroundColor = "red";
                button.style.color = "white";
                
                // Highlight the correct answer
                allButtons.forEach(btn => {
                    if (btn.textContent === correctUser) {
                        btn.style.backgroundColor = "green";
                        btn.style.color = "white";
                    }
                });
            }
        })
        document.getElementById("optionArea").appendChild(button);
        
    });
    /*    
    for randomly selected users + correct user, make a button for each of them
    4 buttons, one of them is the correct user, the other 3 are random users

    */
});