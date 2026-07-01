document.addEventListener("DOMContentLoaded", () => {
    
    // ------------------------------------------------------------------ //
    // 1. Transaction Delete Confirmation Warn                           //
    // ------------------------------------------------------------------ //
    const deleteLinks = document.querySelectorAll(".delete-link");

    deleteLinks.forEach(link => {
        link.addEventListener("click", (event) => {
            const confirmed = confirm("Are you sure you want to delete this expense record? This action cannot be undone.");
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    // ------------------------------------------------------------------ //
    // 2. Video Modal Popup Operations                                   //
    // ------------------------------------------------------------------ //
    const openVideoBtn = document.getElementById("open-video-btn");
    const closeVideoBtn = document.getElementById("close-modal-btn");
    const videoModal = document.getElementById("video-modal");
    const videoIframe = document.getElementById("video-iframe");

    // Clean placeholder personal finance tutorial video
    const youtubeEmbedUrl = "https://www.youtube.com/embed/FkvS1H9630w?autoplay=1";

    if (openVideoBtn && videoModal && videoIframe) {
        // Open modal and load video source
        openVideoBtn.addEventListener("click", () => {
            videoIframe.src = youtubeEmbedUrl;
            videoModal.classList.add("active");
        });

        // Helper to close modal and stop/clear video source
        const closeModal = () => {
            videoModal.classList.remove("active");
            videoIframe.src = ""; // Stops the video playback immediately
        };

        // Close on clicking close button
        if (closeVideoBtn) {
            closeVideoBtn.addEventListener("click", closeModal);
        }

        // Close on clicking the semi-transparent black overlay
        videoModal.addEventListener("click", (e) => {
            if (e.target === videoModal) {
                closeModal();
            }
        });

        // Close on pressing Escape key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && videoModal.classList.contains("active")) {
                closeModal();
            }
        });
    }

    // ------------------------------------------------------------------ //
    // 3. Floating Toast Notifications (Premium UX - Fade In & Out)       //
    // ------------------------------------------------------------------ //
    
    // First, instantly neutralize the parent container's layout footprint
    const container = document.querySelector(".flash-messages-container");
    if (container) {
        container.style.position = "absolute"; // Removes it completely from the page flow
        container.style.margin = "0";
        container.style.padding = "0";
        container.style.height = "0";
        container.style.width = "0";
        container.style.overflow = "visible";
    }

    const flashMessages = document.querySelectorAll(".auth-success, .auth-error");

    flashMessages.forEach(msg => {
        // 1. Instantly convert the alert into a floating toast
        msg.style.position = "fixed";
        msg.style.top = "24px";
        msg.style.left = "50%";
        msg.style.zIndex = "9999";
        msg.style.boxShadow = "0 10px 30px rgba(0, 0, 0, 0.15)";
        msg.style.borderRadius = "8px";
        msg.style.padding = "12px 24px";
        msg.style.width = "calc(100% - 40px)";
        msg.style.maxWidth = "400px";
        msg.style.textAlign = "center";
        msg.style.fontWeight = "500";
        
        // Setup initial invisible state (slightly shifted up)
        msg.style.opacity = "0";
        msg.style.transform = "translate(-50%, -20px)";
        msg.style.transition = "opacity 0.4s ease, transform 0.4s ease";

        // 2. Trigger the Fade-In & Slide-Down animation on the next frame
        requestAnimationFrame(() => {
            msg.style.opacity = "1";
            msg.style.transform = "translate(-50%, 0)";
        });

        // 3. Wait for 2.6 seconds, then Fade-Out & Slide-Up
        setTimeout(() => {
            msg.style.opacity = "0";
            msg.style.transform = "translate(-50%, -20px)";
            
            // 4. Completely remove the element from the DOM after transition completes
            setTimeout(() => {
                msg.remove();
                
                // Clean up the parent container if it's now empty
                if (container && container.children.length === 0) {
                    container.remove();
                }
            }, 400); // 400ms matching transition duration
        }, 2600); // 2.6 seconds delay
    });

});