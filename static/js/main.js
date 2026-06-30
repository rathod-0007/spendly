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
});