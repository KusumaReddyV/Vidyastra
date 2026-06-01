// Frontend behaviors for Resume Analyzer

document.addEventListener('DOMContentLoaded', function() {
    // Drag & Drop for resume upload
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resume');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');

    if (dropzone && fileInput) {
        // Click to browse
        dropzone.addEventListener('click', () => fileInput.click());

        // Drag events
        dropzone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                fileInput.click();
            }
        });

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        // Remove file
        if (removeFile) {
            removeFile.addEventListener('click', () => {
                fileInput.value = '';
                fileInfo.classList.add('d-none');
                dropzone.classList.remove('d-none');
                dropzone.removeAttribute('aria-hidden');
            });
        }
    }

    function handleFileSelect(file) {
        // Validate file type and size
        if (!file.type.includes('pdf')) {
            alert('Please select a PDF file.');
            return;
        }
        if (file.size > 16 * 1024 * 1024) { // 16MB
            alert('File size must be less than 16MB.');
            return;
        }

        // Show file info
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
        dropzone.classList.add('d-none');
        dropzone.setAttribute('aria-hidden', 'true');
    }

    // Character counter for job description
    const jdTextarea = document.getElementById('job_description');
    const jdCounter = document.getElementById('jdCounter');

    if (jdTextarea && jdCounter) {
        jdTextarea.addEventListener('input', () => {
            jdCounter.textContent = jdTextarea.value.length + ' characters';
        });
    }

    // Sample JD button
    const sampleBtn = document.getElementById('sampleJD');
    if (sampleBtn && jdTextarea) {
        sampleBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/sample-jd');
                const data = await response.json();
                jdTextarea.value = data.job_description;
                jdTextarea.dispatchEvent(new Event('input')); // Trigger counter update
            } catch (error) {
                console.error('Error loading sample JD:', error);
                alert('Error loading sample job description.');
            }
        });
    }

    // Submit button loading state
    const submitBtn = document.getElementById('submitBtn');
    const submitBtnText = document.getElementById('submitBtnText');
    const submitBtnLoading = document.getElementById('submitBtnLoading');
    
    if (submitBtn && submitBtnText && submitBtnLoading) {
        const form = document.getElementById('analyzeForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                submitBtnText.classList.add('d-none');
                submitBtnLoading.classList.remove('d-none');
                submitBtn.disabled = true;

                // Re-enable if error (page doesn't redirect)
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtnText.classList.remove('d-none');
                        submitBtnLoading.classList.add('d-none');
                        submitBtn.disabled = false;
                    }
                }, 30000); // 30s timeout
            });
        }
    }

    // Results page actions
    const downloadBtn = document.getElementById('downloadPDF');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            window.print(); // Simple PDF via print
        });
    }

    const shareBtn = document.getElementById('shareResults');
    if (shareBtn) {
        shareBtn.addEventListener('click', async () => {
            const url = window.location.href;
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Resume Analysis Results',
                        text: 'Check out my resume analysis results!',
                        url: url
                    });
                } catch (error) {
                    console.log('Share cancelled');
                }
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(url).then(() => {
                    alert('Link copied to clipboard!');
                }).catch(() => {
                    alert('Share link: ' + url);
                });
            }
        });
    }
});
