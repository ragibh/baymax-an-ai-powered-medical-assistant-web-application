/**
 * Homepage hero video — autoplay muted. User toggles sound via button.
 */
(function () {
    'use strict';

    const video = document.getElementById('bx-hero-bg-video');
    const muteBtn = document.getElementById('bx-hero-mute-btn');
    const progressFill = document.querySelector('.bx-hero-vid-progress .bar-fill');

    if (!video) return;

    video.loop = true;
    video.playsInline = true;
    video.muted = true;
    video.setAttribute('muted', '');

    const updateMuteIcon = () => {
        if (!muteBtn) return;
        const icon = muteBtn.querySelector('i');
        if (icon) {
            icon.className = video.muted ? 'fas fa-volume-xmark' : 'fas fa-volume-high';
        }
        muteBtn.title = video.muted ? 'Turn sound on' : 'Turn sound off';
    };

    const playVideo = () => {
        video.play().catch(() => {});
    };

    muteBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        video.muted = !video.muted;
        if (!video.muted) {
            video.removeAttribute('muted');
        } else {
            video.setAttribute('muted', '');
        }
        if (!video.muted) video.play();
        updateMuteIcon();
    });

    video.addEventListener('timeupdate', () => {
        if (progressFill && video.duration) {
            progressFill.style.width = (video.currentTime / video.duration) * 100 + '%';
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', playVideo);
    } else {
        playVideo();
    }

    document.addEventListener('visibilitychange', () => {
        if (!document.hidden && video.paused) playVideo();
    });

    updateMuteIcon();
})();
