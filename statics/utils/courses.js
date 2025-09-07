export const renderTabsPage = (container) => {
    container.innerHTML = `
      <div style="width: 100%; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <div style="display: flex; border-bottom: 2px solid #eee; flex-wrap: wrap;">
          <button class="tab-btn active" data-tab="tab1" style="flex:1; padding:12px; background:none; border:none; border-bottom:3px solid #4a90e2; color:#4a90e2; font-weight:bold; cursor:pointer;">Education</button>
          <button class="tab-btn" data-tab="tab2" style="flex:1; padding:12px; background:none; border:none; border-bottom:3px solid transparent; color:#555; cursor:pointer;">Entertainment</button>
        </div>
  
        <div id="tab1" class="tab-content" style="padding:20px; display:block;">
          <h3 style="margin-top:0; color:#4a90e2;">Manage Educational content</h3>
          <div style="width:100%;display:flex;flex-direction:column" >
            <div style="width:100%; display:flex;flex-direction:row;justify-content:center;gap:10px;margin-top:40px ">
              <input placeholder="Create Class" style="padding:8px; flex:1; border:1px solid #ccc; border-radius:4px;"/>
              <button style="padding:8px 16px; background:#4a90e2; color:#fff; border:none; border-radius:4px; cursor:pointer;">Create</button>
            </div>
          </div>
        </div>
  
        <div id="tab2" class="tab-content" style="padding:20px; display:none;">
          <h3 style="margin-top:0; color:#4a90e2;">Manage Entertainment content</h3>
          <div style="width:100%;display:flex;flex-direction:column" >
            <div style="width:100%; display:flex;flex-direction:row;justify-content:center;gap:10px;margin-top:40px ">
              <input placeholder="Create New Moovie Group" style="padding:8px; flex:1; border:1px solid #ccc; border-radius:4px;"/>
              <button style="padding:8px 16px; background:#4a90e2; color:#fff; border:none; border-radius:4px; cursor:pointer;">Create</button>
            </div>
          </div>
        </div>
      </div>
    `;

    const tabBtns = container.querySelectorAll(".tab-btn");
    const tabContents = container.querySelectorAll(".tab-content");

    const fetchClsData = async () => {
        try {
            const res = await fetch(`/route/classes/all`, { method: "GET" });

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const clsList = await res.json(); // parse the actual JSON body
            return clsList;
        } catch (err) {
            alert("Something went wrong!");
            console.error("Fetch error:", err);
            return null;
        }
    };

    (async () => {
        const data = await fetchClsData()
        if(data){
            const {classes} = data
            const entertainment = classes && Array.isArray(classes) && classes.length > 0 && classes.filter(i => i.category === "entertainment")
            const academic = classes && Array.isArray(classes) && classes.length > 0 && classes.filter(i => i.category === "academic")
            console.log({
                entertainment,
                academic
            })
            tabBtns.forEach((btn) => {
                btn.addEventListener("click", () => {
                    const target = btn.getAttribute("data-tab");
        
                    // reset all tabs
                    tabBtns.forEach((b) => {
                        b.classList.remove("active");
                        b.style.color = "#555";
                        b.style.borderBottom = "3px solid transparent";
                    });
                    tabContents.forEach((c) => (c.style.display = "none"));
        
                    // activate clicked tab
                    btn.classList.add("active");
                    btn.style.color = "#4a90e2";
                    btn.style.borderBottom = "3px solid #4a90e2";
                    container.querySelector("#" + target).style.display = "block";
                });
            });
        }
    })()
};


