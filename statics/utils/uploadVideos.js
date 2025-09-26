function ___init__() {
    const upload_videos = document.getElementById("upload_videos")
    const contentRenderArea = document.querySelector(".content")
    if (upload_videos) {
        upload_videos.addEventListener("click", (e) => {
            e.preventDefault()
            contentRenderArea.innerHTML = ""
            renderForm(contentRenderArea)
        })
    }
    console.log("hello", upload_videos)
}
___init__()

function renderForm(root) {
    root.innerHTML = `
    <form id="videoForm" class="form-container">
      <!-- Class Dropdown -->
      <div class="form-group">
        <label for="class-select">Select Class Name</label>
        <select id="class-select">
          <option>Select Class</option>
          <option>Option A</option>
          <option>Option B</option>
          <option>Option C</option>
        </select>
      </div>

      <!-- Subject Dropdown -->
      <div class="form-group">
        <label for="subject-select">Select Subject Name</label>
        <select id="subject-select">
          <option>Select Subject</option>
          <option>Option A</option>
          <option>Option B</option>
          <option>Option C</option>
        </select>
      </div>

      <!-- Topic Dropdown -->
      <div class="form-group">
        <label for="topic-select">Select Topic Name</label>
        <select id="topic-select">
          <option>Select Topic</option>
          <option>Option A</option>
          <option>Option B</option>
          <option>Option C</option>
        </select>
      </div>

      <!-- Description Textarea -->
      <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" rows="4" placeholder="Enter description here..."></textarea>
      </div>

      <!-- Video Upload -->
      <div class="form-group">
        <label for="video-upload">Upload Video</label>
        <input type="file" id="video-upload" accept="video/*" />
      </div>

      <!-- Submit Button -->
      <div class="form-group">
        <button type="submit" class="btn-submit">Submit</button>
      </div>
    </form>
    `

    // attach submit listener after rendering
    const form = document.getElementById("videoForm")
    const className = document.getElementById("class-select")
    const subject = document.getElementById("subject-select")
    const topic = document.getElementById("topic-select")
    const description = document.getElementById("description")
    const videoFile = document.getElementById("video-upload")
    let url = null

    populateClassDropdown()
    className.addEventListener("change", (e) => {
        e.preventDefault()
        populateSubjectDropdown()
    })
    subject.addEventListener("change", (e) => {
        e.preventDefault()
        populateTopicsDropdown()
    })
    createLoader()
    videoFile.addEventListener('change', async (e) => {
        e.preventDefault();

        const video = videoFile.files[0];
        if (!video) return;

        const formData = new FormData();
        formData.append("file", video);

        try {
            showLoader(); // show loader while uploading

            const res = await fetch(`/route/video/upload`, {
                method: "POST",
                body: formData
            });

            const data = await res.json()

            if (!data || !data.urls) return
            url = data.urls

            alert("Video uploaded successfully! Check console for response.")
        } catch (error) {
            console.error("Error while uploading video:", error)
            alert("Error while uploading video. Try again!")
        } finally {
            hideLoader()
        }
    });


    form.addEventListener("submit", (e) => {
        e.preventDefault()
        handleFormSubmit(url)
    })

    // Inject styles dynamically (only once)
    if (!document.getElementById("form-styles")) {
        const style = document.createElement("style")
        style.id = "form-styles"
        style.innerHTML = `
          .form-container {
            max-width: 400px;
            margin: 20px auto;
            padding: 16px;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            gap: 16px;
          }

          .form-group {
            display: flex;
            flex-direction: column;
          }

          .form-group label {
            margin-bottom: 6px;
            font-size: 14px;
            font-weight: 600;
            color: #333;
          }

          .form-group select,
          .form-group textarea,
          .form-group input[type="file"] {
            padding: 10px;
            font-size: 14px;
            border-radius: 6px;
            border: 1px solid #ccc;
            background: #f9f9f9;
            transition: border 0.2s ease, box-shadow 0.2s ease;
          }

          .form-group select:focus,
          .form-group textarea:focus,
          .form-group input[type="file"]:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 4px rgba(0,123,255,0.3);
          }

          .form-group textarea {
            resize: vertical;
            min-height: 80px;
          }

          .btn-submit {
            padding: 10px;
            font-size: 15px;
            font-weight: 600;
            color: #fff;
            background-color: #007bff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s ease;
          }

          .btn-submit:hover {
            background-color: #0056b3;
          }

          .btn-submit:focus {
            outline: none;
            box-shadow: 0 0 4px rgba(0,123,255,0.4);
          }

          @media (max-width: 480px) {
            .form-container {
              max-width: 95%;
              padding: 12px;
            }
            .form-group label {
              font-size: 13px;
            }
            .form-group select,
            .form-group textarea,
            .form-group input[type="file"],
            .btn-submit {
              font-size: 13px;
              padding: 8px;
            }
          }
        `
        document.head.appendChild(style)
    }
}

// function invoked on submit
async function handleFormSubmit(url) {
    if(!url){
        alert("Please upload the video")
        return
    }

    const className = document.getElementById("class-select").value
    const subject = document.getElementById("subject-select").value
    const topic = document.getElementById("topic-select").value
    const description = document.getElementById("description").value
    const videoFile = [
        "449323a0-5184-4ac0-8d9d-e5e5e7238914_Udaipur_Files_2025_Hindi_Full_Movie_480p_HDTC-(Filmywap.mov).mp4"
    ]
    console.log({
        className,
        subject,
        topic,
        description,
        videoFile
    })
    showLoader()

    const uploadData = {
        class_ref: Number(className),
        subject_ref: Number(subject),
        topic_ref: Number(topic),
        sl_no: 1,
        video_url: videoFile,
        description: description,
        thumbnailUrl: "null"
    }
    try {
        const res = await fetch(`/route/video/create`, {
            method: "post",
            body: JSON.stringify(uploadData),
            headers: {
                "Content-Type": "application/json" // MUST have this
            }
        })
        const data = await res.json()
        if(!res.ok){
            alert("Error while upload")
            return
        }
        alert("Video upload successfully")
        document.getElementById("dashboard").click()
    } catch (error) {
        alert("Error while upload video")
    } finally {
        hideLoader()
    }

}
async function populateTopicsDropdown() {
    const topicSelect = document.getElementById("topic-select")
    const subject = document.getElementById("subject-select").value
    if (!subject) return

    try {
        const res = await fetch(`/route/topics/all/${subject}`, {
            method: "get"
        })
        const data = await res.json()
        if (!data || !Array.isArray(data)) {
            console.error("Error fetching classes:", error);
            topicSelect.innerHTML = '<option>No Subject Found under this class</option>'
            return
        }
        topicSelect.innerHTML = '<option>Select Class</option>';
        data.forEach(cls => {
            const option = document.createElement("option");
            option.value = cls.id;
            option.textContent = cls.topic_name;
            topicSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching classes:", error);
        topicSelect.innerHTML = '<option>Error loading classes</option>';
    }
}
async function populateSubjectDropdown() {
    const subjectSelect = document.getElementById("subject-select")
    const className = document.getElementById("class-select").value
    if (!className) return

    try {
        const res = await fetch(`/route/subjects/all/${className}`, {
            method: "get"
        })
        const data = await res.json()
        if (!data || !data.list) {
            console.error("Error fetching classes:", error);
            subjectSelect.innerHTML = '<option>No Subject Found under this class</option>'
            return
        }
        subjectSelect.innerHTML = '<option>Select Class</option>';
        data.list.forEach(cls => {
            const option = document.createElement("option");
            option.value = cls.id;
            option.textContent = cls.subject_name;
            subjectSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching classes:", error);
        subjectSelect.innerHTML = '<option>Error loading classes</option>';
    }
}
async function populateClassDropdown() {
    const classSelect = document.getElementById("class-select");

    try {
        const res = await fetch("/route/classes/all", { method: "GET" });
        const data = await res.json();

        if (!data || !data.classes) return

        classSelect.innerHTML = '<option>Select Class</option>';
        data.classes.forEach(cls => {
            const option = document.createElement("option");
            option.value = cls.id; // or cls.name depending on your API
            option.textContent = cls.class_name;
            classSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching classes:", error);
        classSelect.innerHTML = '<option>Error loading classes</option>';
    }
}

function createLoader() {
    if (document.getElementById("common-loader")) return;

    const loader = document.createElement("div");
    loader.id = "common-loader";
    loader.style.display = "none";
    loader.innerHTML = `
      <div class="loader-overlay">
        <div class="loader-spinner"></div>
      </div>
    `;
    document.body.appendChild(loader);

    const style = document.createElement("style");
    style.id = "loader-styles";
    style.innerHTML = `
      .loader-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
      }
      .loader-spinner {
        width: 50px;
        height: 50px;
        border: 6px solid #f3f3f3;
        border-top: 6px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      @keyframes spin {
        0% { transform: rotate(0deg);}
        100% { transform: rotate(360deg);}
      }
      @media (max-width: 480px) {
        .loader-spinner {
          width: 40px;
          height: 40px;
          border-width: 5px;
        }
      }
    `;
    document.head.appendChild(style);
}

function showLoader() {
    const loader = document.getElementById("common-loader");
    if (loader) loader.style.display = "flex";
}

// Hide loader
function hideLoader() {
    const loader = document.getElementById("common-loader");
    if (loader) loader.style.display = "none";
}