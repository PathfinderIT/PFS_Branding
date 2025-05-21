import os
import mimetypes
import html
import urllib.parse
from datetime import datetime
from jinja2 import Template
import json

# Initialize mimetypes
mimetypes.init()

# Get repository and branch information from environment variables
REPO = os.environ.get('GITHUB_REPOSITORY', 'username/repo')
BRANCH = os.environ.get('GITHUB_REF_NAME', 'main')

def get_cdn_url(filepath):
    """Generate a proper CDN URL for the file"""
    path_parts = filepath.split('/')
    encoded_parts = [urllib.parse.quote(part) for part in path_parts]
    encoded_path = '/'.join(encoded_parts)
    return f'https://raw.githack.com/{REPO}/{BRANCH}/{encoded_path}'

def is_image(filepath):
    """Check if file is an image based on mimetype"""
    mime, _ = mimetypes.guess_type(filepath)
    return mime and mime.startswith('image/')

def is_text(filepath):
    """Check if file is a text file"""
    mime, _ = mimetypes.guess_type(filepath)
    return mime and (mime.startswith('text/') or 'json' in mime or 'xml' in mime or filepath.endswith('.md'))

def get_file_icon(filepath):
    """Return appropriate icon class based on file extension"""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    icons = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
        'code': ['.html', '.htm', '.css', '.js', '.ts', '.jsx', '.tsx', '.php', '.py', '.rb', '.java', '.c', '.cpp', '.go'],
        'pdf': ['.pdf'],
        'word': ['.doc', '.docx'],
        'excel': ['.xls', '.xlsx', '.csv'],
        'powerpoint': ['.ppt', '.pptx'],
        'archive': ['.zip', '.rar', '.tar', '.gz', '.7z'],
        'text': ['.txt', '.md', '.rtf'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.webm'],
        'audio': ['.mp3', '.wav', '.ogg', '.flac'],
        'font': ['.ttf', '.otf', '.woff', '.woff2'],
    }
    
    for icon_type, extensions in icons.items():
        if ext in extensions:
            return f"fa-file-{icon_type}"
    
    return "fa-file"

def format_filesize(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB"

def main():
    # Collect file data
    file_data = []
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and files and specific directories
        if (root.startswith('./.git') or 
            '/.' in root or 
            root.startswith('./.github/workflows') or 
            'node_modules' in root):
            continue
            
        for file in files:
            # Skip hidden files and our output file
            if file.startswith('.') or file == 'cdn-preview.html':
                continue
                
            filepath = os.path.join(root, file).replace('./', '')
            
            try:
                cdn_url = get_cdn_url(filepath)
                file_size = os.path.getsize(filepath)
                is_img = is_image(filepath)
                file_icon = get_file_icon(filepath)
                
                # Skip very large files from preview (optional)
                if file_size > 10 * 1024 * 1024:  # 10MB
                    continue
                
                file_data.append({
                    'path': filepath,
                    'name': os.path.basename(filepath),
                    'cdn_url': cdn_url,
                    'is_image': is_img,
                    'icon': file_icon,
                    'size': format_filesize(file_size),
                    'size_bytes': file_size,
                    'extension': os.path.splitext(filepath)[1].lower(),
                })
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    
    # Sort files by path
    file_data.sort(key=lambda x: x['path'])
    
    # Read the template file or use a default template
    template_path = '.github/templates/cdn_template.html'
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    else:
        # If no template exists, use the default one
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CDN Files Preview - {{ repo }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        :root {
            --bs-primary: #3d7a4e;    /* Main green */
            --bs-primary-rgb: 61, 122, 78;
            --bs-secondary: #90a960;  /* Light green */
            --bs-secondary-rgb: 144, 169, 96;
            --bs-accent: #f17a54;     /* Coral accent */
            --bs-accent-rgb: 241, 122, 84;
            --bs-info: #7a89c4;       /* Blue accent */
            --bs-info-rgb: 122, 137, 196;
            --bs-light: #e6dec6;      /* Light beige */
            --bs-light-rgb: 230, 222, 198;
            --bs-lighter: #ede4c6;    /* Lighter beige */
            --bs-lighter-rgb: 237, 228, 198;
        }
        
        body {
            background-color: #f9f9f9;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        
        .header {
            background: linear-gradient(135deg, var(--bs-primary) 0%, #2c5e41 100%);
            color: white;
            padding: 2.5rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .search-container {
            position: sticky;
            top: 0;
            padding: 1rem;
            background-color: rgba(255, 255, 255, 0.95);
            z-index: 1000;
            backdrop-filter: blur(10px);
            border-bottom: 1px solid #dee2e6;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
            border-radius: 0 0 10px 10px;
        }
        
        .file-card {
            border-radius: 10px;
            border: 1px solid #e9ecef;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            height: 100%;
            background-color: white;
        }
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .preview-container {
            height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f8f9fa;
            overflow: hidden;
            border-bottom: 1px solid #e9ecef;
        }
        
        .preview-image {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .preview-icon {
            font-size: 3rem;
            color: #adb5bd;
        }
        
        .file-details {
            padding: 1.25rem;
        }
        
        .file-name {
            font-weight: 600;
            font-size: 1.1rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 0.5rem;
        }
        
        .file-path {
            font-size: 0.8rem;
            color: #6c757d;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 0.75rem;
        }
        
        .file-size {
            font-size: 0.85rem;
            color: #6c757d;
            margin-bottom: 1rem;
        }
        
        .copy-btn {
            width: 100%;
            border-radius: 6px;
            border: none;
            background-color: var(--bs-primary);
            transition: background-color 0.2s;
        }
        
        .copy-btn:hover {
            background-color: #2c5e41;
        }
        
        .filters {
            margin-bottom: 2rem;
        }
        
        .filter-btn {
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
            border-radius: 20px;
            padding: 0.4rem 1rem;
            transition: all 0.2s;
        }
        
        .filter-btn.active {
            background-color: var(--bs-primary);
            border-color: var(--bs-primary);
            box-shadow: 0 4px 8px rgba(61, 122, 78, 0.2);
        }
        
        .view-toggle {
            margin-right: 1rem;
        }
        
        .view-toggle .btn {
            border-radius: 4px;
        }
        
        .no-results {
            text-align: center;
            padding: 5rem 1rem;
            color: #6c757d;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            display: none;
        }
        
        .grid-view .file-card {
            margin-bottom: 1.5rem;
        }
        
        .list-view .preview-container {
            height: 40px;
            width: 40px;
        }
        
        .list-view .file-card {
            margin-bottom: 0.5rem;
        }
        
        footer {
            margin-top: 3rem;
            padding: 2rem 0;
            background-color: #f1f3f5;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }
        
        .footer-link {
            color: var(--bs-primary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }
        
        .footer-link:hover {
            color: #2c5e41;
        }
        
        @media (max-width: 768px) {
            .preview-container {
                height: 120px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>CDN Files Preview</h1>
            <p class="mb-0">Repository: {{ repo }} (Branch: {{ branch }})</p>
        </div>
    </div>
    
    <div class="container">
        <div class="search-container">
            <div class="row align-items-center">
                <div class="col-md-6 mb-3 mb-md-0">
                    <input type="text" id="searchInput" class="form-control" placeholder="Search for files by name or path...">
                </div>
                <div class="col-md-6 d-flex justify-content-md-end align-items-center">
                    <div class="btn-group view-toggle" role="group">
                        <button type="button" class="btn btn-outline-secondary active" id="gridViewBtn">
                            <i class="fas fa-th-large"></i>
                        </button>
                        <button type="button" class="btn btn-outline-secondary" id="listViewBtn">
                            <i class="fas fa-list"></i>
                        </button>
                    </div>
                    <span class="text-muted ms-3">
                        <span id="fileCount">{{ file_count }}</span> files
                    </span>
                </div>
            </div>
        </div>
        
        <div class="filters">
            <div class="d-flex flex-wrap">
                <button class="btn btn-sm btn-outline-secondary filter-btn active" data-filter="all">All Files</button>
                <button class="btn btn-sm btn-outline-secondary filter-btn" data-filter="image">Images</button>
                <button class="btn btn-sm btn-outline-secondary filter-btn" data-filter="code">Code</button>
                <button class="btn btn-sm btn-outline-secondary filter-btn" data-filter="document">Documents</button>
                <button class="btn btn-sm btn-outline-secondary filter-btn" data-filter="other">Other</button>
            </div>
        </div>
        
        <div id="fileGrid" class="row grid-view">
            <!-- File cards will be dynamically added here -->
        </div>
        
        <div id="fileList" class="list-view" style="display: none;">
            <!-- File list will be dynamically added here -->
        </div>
        
        <div class="no-results">
            <h3>No matching files found</h3>
            <p>Try adjusting your search criteria</p>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>Generated on {{ date }} by GitHub Actions</p>
            <p>
                <a href="https://raw.githack.com/" target="_blank" class="footer-link">
                    Powered by raw.githack.com
                </a>
            </p>
        </div>
    </footer>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    <script>
        // File data
        const fileData = {{ file_data_json|safe }};
        
        // DOM elements
        const searchInput = document.getElementById('searchInput');
        const fileGrid = document.getElementById('fileGrid');
        const fileList = document.getElementById('fileList');
        const fileCountElement = document.getElementById('fileCount');
        const noResults = document.querySelector('.no-results');
        const gridViewBtn = document.getElementById('gridViewBtn');
        const listViewBtn = document.getElementById('listViewBtn');
        const filterButtons = document.querySelectorAll('.filter-btn');
        
        // Current filter
        let currentFilter = 'all';
        let currentView = 'grid';
        
        // Helper function to get file type category
        function getFileCategory(file) {
            if (file.is_image) return 'image';
            
            const codeExtensions = ['.html', '.css', '.js', '.ts', '.jsx', '.tsx', '.php', '.py', '.rb', '.java', '.c', '.cpp', '.go'];
            const documentExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.rtf'];
            
            if (codeExtensions.includes(file.extension)) return 'code';
            if (documentExtensions.includes(file.extension)) return 'document';
            
            return 'other';
        }
        
        // Render files in grid view
        function renderGridView(files) {
            fileGrid.innerHTML = '';
            
            files.forEach(file => {
                const fileCard = document.createElement('div');
                fileCard.className = 'col-md-6 col-lg-4 col-xl-3 grid-view-item';
                fileCard.dataset.category = getFileCategory(file);
                
                const preview = file.is_image 
                    ? `<img src="${file.cdn_url}" class="preview-image" alt="${file.name}" loading="lazy">` 
                    : `<i class="fas ${file.icon} preview-icon"></i>`;
                
                fileCard.innerHTML = `
                    <div class="file-card">
                        <div class="preview-container">
                            ${preview}
                        </div>
                        <div class="file-details">
                            <div class="file-name" title="${file.name}">${file.name}</div>
                            <div class="file-path" title="${file.path}">${file.path}</div>
                            <div class="file-size">${file.size}</div>
                            <button class="btn btn-sm btn-primary mt-2 copy-btn" data-url="${file.cdn_url}">
                                <i class="fas fa-copy"></i> Copy URL
                            </button>
                        </div>
                    </div>
                `;
                
                fileGrid.appendChild(fileCard);
            });
            
            // Add event listeners to copy buttons
            document.querySelectorAll('.copy-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const url = this.getAttribute('data-url');
                    navigator.clipboard.writeText(url).then(() => {
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        
                        setTimeout(() => {
                            this.innerHTML = originalText;
                        }, 1500);
                    });
                });
            });
        }
        
        // Render files in list view
        function renderListView(files) {
            fileList.innerHTML = '';
            
            const table = document.createElement('table');
            table.className = 'table table-hover';
            
            table.innerHTML = `
                <thead>
                    <tr>
                        <th style="width: 50px"></th>
                        <th>Name</th>
                        <th>Path</th>
                        <th>Size</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody></tbody>
            `;
            
            const tbody = table.querySelector('tbody');
            
            files.forEach(file => {
                const row = document.createElement('tr');
                row.dataset.category = getFileCategory(file);
                
                const preview = file.is_image 
                    ? `<img src="${file.cdn_url}" class="img-thumbnail" style="width: 32px; height: 32px; object-fit: contain;" alt="${file.name}" loading="lazy">` 
                    : `<i class="fas ${file.icon}" style="font-size: 1.2rem;"></i>`;
                
                row.innerHTML = `
                    <td class="text-center">${preview}</td>
                    <td>${file.name}</td>
                    <td><small class="text-muted">${file.path}</small></td>
                    <td>${file.size}</td>
                    <td>
                        <button class="btn btn-sm btn-primary copy-btn" data-url="${file.cdn_url}">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </td>
                `;
                
                tbody.appendChild(row);
            });
            
            fileList.appendChild(table);
            
            // Add event listeners to copy buttons
            document.querySelectorAll('.copy-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const url = this.getAttribute('data-url');
                    navigator.clipboard.writeText(url).then(() => {
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        
                        setTimeout(() => {
                            this.innerHTML = originalText;
                        }, 1500);
                    });
                });
            });
        }
        
        // Filter files
        function filterFiles() {
            const searchTerm = searchInput.value.toLowerCase();
            
            const filteredFiles = fileData.filter(file => {
                const nameMatch = file.name.toLowerCase().includes(searchTerm);
                const pathMatch = file.path.toLowerCase().includes(searchTerm);
                const categoryMatch = currentFilter === 'all' || getFileCategory(file) === currentFilter;
                
                return (nameMatch || pathMatch) && categoryMatch;
            });
            
            fileCountElement.textContent = filteredFiles.length;
            
            if (filteredFiles.length === 0) {
                noResults.style.display = 'block';
                fileGrid.style.display = 'none';
                fileList.style.display = 'none';
            } else {
                noResults.style.display = 'none';
                
                if (currentView === 'grid') {
                    fileGrid.style.display = 'flex';
                    fileList.style.display = 'none';
                    renderGridView(filteredFiles);
                } else {
                    fileGrid.style.display = 'none';
                    fileList.style.display = 'block';
                    renderListView(filteredFiles);
                }
            }
        }
        
        // Initialize
        function init() {
            // Initial render
            renderGridView(fileData);
            renderListView(fileData);
            filterFiles();
            
            // Search functionality
            searchInput.addEventListener('input', filterFiles);
            
            // View toggle
            gridViewBtn.addEventListener('click', function() {
                if (currentView !== 'grid') {
                    currentView = 'grid';
                    listViewBtn.classList.remove('active');
                    gridViewBtn.classList.add('active');
                    filterFiles();
                }
            });
            
            listViewBtn.addEventListener('click', function() {
                if (currentView !== 'list') {
                    currentView = 'list';
                    gridViewBtn.classList.remove('active');
                    listViewBtn.classList.add('active');
                    filterFiles();
                }
            });
            
            // Filter buttons
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const filter = this.getAttribute('data-filter');
                    
                    // Update UI
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Update filter and re-render
                    currentFilter = filter;
                    filterFiles();
                });
            });
        }
        
        // Start the app
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>'''
    
    # Create template renderer
    template = Template(template_content)
    
    # Render template with data
    rendered_html = template.render(
        repo=REPO,
        branch=BRANCH,
        file_count=len(file_data),
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        file_data_json=json.dumps(file_data)
    )
    
    # Write the HTML file
    with open('cdn-preview.html', 'w', encoding='utf-8') as f:
        f.write(rendered_html)
    
    print("✅ Generated cdn-preview.html successfully with {} files".format(len(file_data)))

if __name__ == "__main__":
    main()
