const apiHost = location.hostname || "127.0.0.1";
const apiBase = `http://${apiHost}:8000`;
const startButton = document.getElementById("startGame");
const mergeToggle = document.getElementById("mergeBursts");
const filterToggle = document.getElementById("filterShort");
const balanceToggle = document.getElementById("balanceUsers");

const MERGE_WINDOW_MINUTES = 2;
const MIN_MESSAGE_WORDS = 3;

let correctUser = "";
let allUsers = [];
let isLoading = false;

// Fetch the users from backend and store them in the allUsers
async function getUsers() {
    const response = await fetch(`${apiBase}/user`);
    allUsers = await response.json();
}


async function startGame() {
    if (isLoading) {
        return;
    }
    isLoading = true;
    try {
        //clear up the message and options area
        document.getElementById("message").innerHTML = "";
        document.getElementById("optionArea").innerHTML = "";

        // If we don't have the users we fetch if we have them we don't fetch
        if (allUsers.length === 0){
            await getUsers();
        }
        
        const mergeBursts = mergeToggle ? mergeToggle.checked : true;
        const minWords = filterToggle && filterToggle.checked ? MIN_MESSAGE_WORDS : 0;
        const balanceUsers = balanceToggle ? balanceToggle.checked : false;
        const messageUrl = new URL(`${apiBase}/message`);
        messageUrl.searchParams.set("merge", mergeBursts ? "true" : "false");
        messageUrl.searchParams.set("merge_window", MERGE_WINDOW_MINUTES.toString());
        messageUrl.searchParams.set("min_words", minWords.toString());
        messageUrl.searchParams.set("balance_users", balanceUsers ? "true" : "false");

        //Fetch random message
        const response = await fetch(messageUrl)
        const data = await response.json();

        correctUser = data.user;

        // Get the HTML elements
        const messageEl = document.getElementById("message");
        const imageEl = document.getElementById("messageImage");
        const audioEl = document.getElementById("messageAudio");

        // Reset everything to hidden/empty initially
        imageEl.style.display = "none";
        imageEl.src = "";
        audioEl.style.display = "none";
        audioEl.src = "";

        const messageText = data.message ?? "";
        const hasMessageText = messageText.trim().length > 0;

        if (data.image) {
            const mediaUrl = `${apiBase}${data.image}`;

            const lowerImage = data.image.toLowerCase();
            const audioExts = [".opus", ".mp3", ".m4a", ".ogg", ".wav"];
            const imageExts = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"];

            if (audioExts.some(ext => lowerImage.endsWith(ext))) {
                audioEl.src = mediaUrl;
                audioEl.style.display = "block";
                messageEl.textContent = hasMessageText ? messageText : "🔊 [Audio Message]";
            } else if (imageExts.some(ext => lowerImage.endsWith(ext))) {
                imageEl.src = mediaUrl;
                imageEl.style.display = "block";
                messageEl.textContent = hasMessageText ? messageText : "📷 [Image Message]";
            } else {
                messageEl.textContent = hasMessageText
                    ? messageText
                    : `📎 [Attached File: ${data.image.split('/').pop()}]`;
            }
        } else {
                messageEl.textContent = messageText;
        }

        messageEl.style.color = "aliceblue";
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
                if (button.dataset.nextReady === "true") {
                    void startGame();
                    return;
                }

                const allButtons = document.querySelectorAll(".optionButton");
                allButtons.forEach(btn => btn.disabled = true);
                let correctButton = null;

                if (user === correctUser) {
                    button.style.backgroundColor = "green";
                    button.style.color = "white";
                    correctButton = button;
                } else {
                    button.style.backgroundColor = "red";
                    button.style.color = "white";
                    
                    // Highlight the correct answer
                    allButtons.forEach(btn => {
                        if (btn.textContent === correctUser) {
                            btn.style.backgroundColor = "green";
                            btn.style.color = "white";
                            correctButton = btn;
                        }
                    });
                }

                if (correctButton) {
                    correctButton.disabled = false;
                    correctButton.dataset.nextReady = "true";
                    correctButton.title = "Click again for next message";
                }
            })
            document.getElementById("optionArea").appendChild(button);
            
        });
        /*    
        for randomly selected users + correct user, make a button for each of them
        4 buttons, one of them is the correct user, the other 3 are random users

        */
    } finally {
        isLoading = false;
    }
}

startButton.addEventListener("click", () => {
    void startGame();
});