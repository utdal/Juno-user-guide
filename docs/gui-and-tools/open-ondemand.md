# Open OnDemand

Open OnDemand provides a web-based interface to access Juno resources without installing additional software. It's the recommended way to run graphical and interactive applications, and works well even on slow networks or from places that block SSH.

## Accessing Open OnDemand

1. Open your web browser
2. Navigate to: [https://juno-ood.hpcre.utdallas.edu/](https://juno-ood.hpcre.utdallas.edu/)
3. Log in with your Juno credentials
4. You'll see the Open OnDemand dashboard

![Screenshot of the Open OnDemand dashboard showing the top navigation bar with Files, Jobs, Clusters, and Interactive Apps menus.](../images/screenshot-ood-dashboard.png)

!!! tip
    Open OnDemand is perfect for users who prefer graphical interfaces or need to access Juno from networks that block SSH.

## Dashboard Features

**Files**

- Browse your home directory
- Upload/download files
- Edit text files directly in browser
- Create new directories

**Jobs**

- View active jobs
- Job composer for creating job scripts
- Job templates

**Clusters**

- Shell access (web-based terminal)
- No SSH client needed

**Interactive Apps**

- Pre-configured GUI applications
- Launch with a few clicks

## Launching Interactive Apps

### Available Applications

Common interactive apps include:

- Jupyter Notebook/Lab
- RStudio
- Desktop (full Linux desktop environment)
- VSCode Server

### Starting an Interactive App

1. Click **Interactive Apps** in the top menu
2. Select your desired application (e.g., "Jupyter Notebook")

   ![Screenshot of the Interactive Apps dropdown menu listing available applications including Jupyter Lab, RStudio, Desktop, and VSCode Server.](../images/screenshot-ood-interactive-apps.png)

3. Fill in the resource request form:
   - **Number of hours**: How long you need (e.g., 2, 4, 8)
   - **Number of cores**: CPUs needed (typically 1-4 for interactive work)
   - **Memory (GB)**: RAM required (e.g., 4, 8, 16)
   - **Partition**: Usually "normal" for CPU, "h100" or "a30" for GPU work

   ![Screenshot of the interactive app resource request form showing fields for hours, cores, memory, and partition.](../images/screenshot-ood-launch-form.png)

4. Click **Launch**

5. Wait for resources to be allocated (you'll see status: Queued → Starting → Running)

   ![Screenshot of the My Interactive Sessions page showing a session card with status transitioning from Queued to Running, and a Connect button.](../images/screenshot-ood-my-sessions.png)

6. Click **Connect to [Application]** when ready

#### Jupyter Notebook Example

```
Interactive Apps → Jupyter Notebook

Settings:
- Number of hours: 4
- Number of cores: 2  
- Memory: 8GB
- Partition: normal

Launch → Wait for allocation → Connect to Jupyter
```

Your Jupyter session opens in a new browser tab running on a compute node!

#### RStudio Example

```
Interactive Apps → RStudio

Settings:
- Number of hours: 2
- Number of cores: 4
- Memory: 16GB
- Partition: normal

Launch → Connect to RStudio
```

## Managing Interactive Sessions

**View Active Sessions**:

- Go to "My Interactive Sessions"
- See all running interactive apps
- Click "Delete" to end session early
- Click application link to reconnect

**Best Practices**:

- Request only the resources you need
- End sessions when finished (don't waste resources)
- Sessions automatically end when time expires

## File Management via Web

**Upload Files**:

1. Click **Files** → **Home Directory**
2. Navigate to destination folder
3. Click **Upload** button
4. Select files from your computer

**Download Files**:

1. Navigate to file location
2. Check the box next to file(s)
3. Click **Download**

**Edit Files**:

1. Click on text file
2. Click **Edit** button
3. Make changes in browser
4. Click **Save**

![Screenshot of the Open OnDemand file manager showing a directory listing with Upload, Download, and Edit buttons, and a breadcrumb navigation bar.](../images/screenshot-ood-file-manager.png)

!!! note
    The upload/download limit is 10GB/file

## Example Workflows

### Jupyter Notebook via OnDemand

1. Open browser → OnDemand portal
2. Interactive Apps → Jupyter Notebook
3. Request: 4 hours, 2 cores, 8GB, normal partition
4. Launch and connect
5. Work in notebook
6. Save files
7. End session when done

### RStudio via OnDemand

1. OnDemand portal → Interactive Apps → RStudio Server
2. Configure: 3 hours, 4 cores, 12GB
3. Launch
4. Connect to RStudio
5. Load your R scripts and data
6. Run analyses
7. Save results
8. End session

## Open OnDemand vs X11

| Feature | Open OnDemand | X11 Forwarding |
|---------|---------------|----------------|
| **Setup** | Just a browser | Requires X server install |
| **Performance** | Better for slow networks | Can be slow over internet |
| **Applications** | Pre-configured apps | Any GUI program |
| **File Management** | Easy web interface | Command line |
| **Session Persistence** | Survives browser close | Closes with SSH disconnect |
| **Best For** | Most users, interactive work | Power users, specific tools |

Need a GUI program that isn't available as an interactive app? See [Launching GUI Programs (X11)](gui-programs.md).

## Next Steps

- [Set up VSCode for remote development →](vscode.md)
- [Launch JupyterLab →](jupyter.md)
- [Learn about containerized applications →](../advanced/containers.md)

## Need Help?

- **Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **HPC Services**: [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)
- **Open a ticket**: For specific GUI application requests or issues
