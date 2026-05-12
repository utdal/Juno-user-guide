# Getting Help

## Overview

The HPC support team is here to help you make the most of Juno. This page explains how to get assistance with technical issues, software requests, and general questions.

## Support Channels

### HPC Services Page

Visit: **[hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)**

This is your primary portal for all HPC support needs.

**What you'll find**:

- Contact information
- Service tiles for different systems (Juno, Ganymede, etc.)
- Quick links to request specific services
- Documentation and resources

### Opening a Support Ticket

The most efficient way to get help is through our ticketing system.

#### How to Open a Ticket

1. **Navigate** to [hpc.utdallas.edu/services](https://hpc.utdallas.edu/services)

2. **Locate** the appropriate system tile:
   - Juno (for Juno-specific issues)
   - Ganymede2 (for Ganymede 2-specific issues)
   - General HPC Services (for general questions)

3. **Click** on the service you need:
   - **General User Support**: Most common - technical issues, usage questions, troubleshooting
   - **Software Installation**: Request new software or specific versions
   - **Add New Account**: Request a new account
   - **Training**: Request training sessions or documentation

4. **Fill out** the web form template:
   - Clear subject line
   - Detailed description of issue/request
   - Steps to reproduce (for errors)
   - Relevant job IDs or file paths
   - Any error messages (copy/paste exact text)

5. **Submit** the ticket

Your ticket is automatically sorted and assigned to the appropriate team member for quick response.

### Direct Email Support

If you're unsure which service to request or need immediate guidance:

**Email**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)

**When to use direct email**:

- Urgent issues affecting active jobs
- Unclear which service category to use
- Follow-up on existing ticket
- General inquiries

## What to Include in Support Requests

### For Technical Issues

Provide as much detail as possible:

```
Subject: SLURM job fails with memory error

Description:
- Job ID: 12345
- Submission date: 2024-01-15 10:30 AM
- Error message: [paste exact error]
- Job script location: /home/username/jobs/job.sh
- Steps taken: Tried increasing memory from 8GB to 16GB
- Still experiencing issue

Expected behavior: Job should complete successfully
Actual behavior: Job terminates with exit code 137

Attached: job script and error log
```

### For Software Requests

**Include**:

- Software name and version
- Purpose/use case
- Required dependencies
- Urgency/timeline
- Whether you've tried module load
- Link to software website/documentation

**Example**:
```
Subject: Request for TensorFlow 2.14 installation

I need TensorFlow 2.14 with GPU support for deep learning research.

Requirements:
- TensorFlow 2.14
- CUDA 12.4 support
- Python 3.9 or 3.10
- cuDNN 8.6

Timeline: Needed for experiments starting next week

I checked with 'module avail tensorflow' and only see version 2.10.

Reference: https://www.tensorflow.org/install
```

### For Account Issues

**Specify**:

- NetID or username
- Nature of issue (can't login, quota exceeded, etc.)
- When problem started
- Any error messages
- What you've already tried

## Response Times

### Standard Support Tickets

- **Initial response**: Within 1 business day
- **Resolution**: Depends on complexity
  - Simple questions: Same day
  - Software installations: 2-5 business days
  - Complex issues: 1-2 weeks

### Urgent Issues

For time-sensitive problems affecting active research:

1. Open a ticket clearly marked as **URGENT**
2. Follow up with email to [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
3. Provide deadline context

We prioritize:

- Production runs with deadlines
- Grant-funded research time constraints
- Issues affecting multiple users

### Office Hours & In-Person Support

The HPC support team operates during business hours (M-F, 8AM–5PM CST). You can visit us in person at **AD 3.206** (Administration Building).

**Emergency contacts**:

- Available for critical cluster-wide issues
- Contact information provided in account welcome email

## Common Support Categories

### 1. General User Support

**Use for**:

- How-to questions
- Job submission issues
- Performance optimization advice
- SLURM errors
- Module problems
- Storage questions
- Login issues

**Example tickets**:

- "How do I request GPU resources?"
- "My job is pending - what's wrong?"
- "Need help optimizing parallel code"

### 2. Software Installation

**Use for**:

- New software requests
- Version updates
- Compiler issues
- Library dependencies

**What we provide**:

- Centrally installed software via modules
- Guidance for user installations
- Container support

### 3. Training and Documentation

**Use for**:

- Orientation session scheduling
- Custom training requests
- Documentation improvements
- Tutorial requests

**Available**:

- Juno Orientation (recorded sessions)
- One-on-one consultations
- Workshops on specific topics

### 4. Storage and Data

**Use for**:

- Quota increases
- Data transfer assistance
- Backup inquiries
- File system issues

### 5. Account Management

**Use for**:

- New account requests
- Group management
- Access modifications
- Password resets

## Self-Help Resources

Before opening a ticket, check if your question is answered in existing resources:

### Documentation

**Primary docs**: [hpc.utdallas.edu](https://hpc.utdallas.edu)

- User guides
- Quick start guides
- Best practices
- FAQ sections

### Recorded Sessions

**Juno Orientation**: Available on documentation site

- Covers basics of using Juno
- SLURM job submission
- Storage and data management
- Fair share system

### Knowledge Base

Common topics documented:

- Module system usage
- Job script examples
- Troubleshooting guides
- Software-specific guides

## Community Resources

### Office Hours

Check the HPC Services page for scheduled office hours:

- Drop-in virtual sessions
- Ask questions in real-time
- Get immediate guidance

### Workshops and Training

Periodic workshops on:

- Introduction to HPC
- Parallel programming with OpenMP and MPI
- Python on HPC
- Containers
- Performance optimization

Subscribe to HPC mailing list for announcements.

## Consultation Services

### Available Consultations

**One-on-one sessions** for:

- Code optimization
- Workflow design
- Scaling studies
- Software architecture
- Grant proposal support

**Request consultation**:

- Open ticket → "Consultation Request"
- Describe your project and needs
- We'll schedule a meeting

### What to Prepare

For effective consultations:
1. **Project overview**: Brief description of research
2. **Current approach**: What you're doing now
3. **Challenges**: Specific problems or goals
4. **Code samples**: If seeking optimization help
5. **Timeline**: Any deadlines or milestones

## Providing Feedback

We value your input to improve services:

### Thumbs Down Button

At the bottom of every response in documentation or tickets:

- Click thumbs down if unhelpful
- Provide specific feedback
- Helps us improve

### Surveys

Periodic user satisfaction surveys:

- Share your experience
- Suggest improvements
- Identify needs

### Direct Feedback

Email suggestions to [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu):

- Documentation improvements
- New features requests
- Service enhancements

## Tips for Effective Support Requests

### Do ✓

- **Be specific**: Exact error messages, job IDs, file paths
- **Include context**: What you're trying to accomplish
- **Show work**: What you've already tried
- **Attach files**: Relevant scripts, logs (if not too large)
- **Follow up**: Respond to questions from support team
- **Close tickets**: Mark resolved when issue is fixed

### Don't ✗

- **Be vague**: "It doesn't work" without details
- **Rush**: Allow time for thorough investigation
- **Duplicate**: Don't open multiple tickets for same issue
- **Assume**: If unsure, ask rather than guess
- **Delay**: Report issues promptly, not weeks later

## Escalation Process

If your issue isn't being resolved:

1. **Reply to ticket**: Request status update
2. **Email support**: Reference ticket number
3. **Request supervisor**: Ask for escalation if needed

We're committed to resolving all issues satisfactorily.

## Emergency Contacts

### Cluster-Wide Issues

If you notice problems affecting everyone:

- Cluster unreachable
- File system failures
- Widespread job failures

**Report immediately**:

- Email [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- Mark as URGENT
- Describe the issue and impact

### Security Concerns

**Report immediately** if you observe:

- Unauthorized access attempts
- Suspicious activity in your account
- Compromised credentials
- Security vulnerabilities

**Contact**: 

- [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- UT Dallas IT Security: [infosecurity@utdallas.edu](mailto:infosecurity@utdallas.edu)

## Additional Resources

### UT Dallas Resources

- **OIT Help Desk**: For NetID, VPN, general IT
- **Research Computing**: For data storage, high-level consulting
- **Graduate School**: For graduate student resources

### External Resources

- **SLURM Documentation**: [slurm.schedmd.com](https://slurm.schedmd.com)

---

**Remember**: The HPC support team is here to help you succeed. Don't hesitate to reach out with questions - there are no "stupid" questions, and we prefer to help early rather than after problems compound.

## Next Steps

- [Review FAQ for common questions →](faq.md)
- [Return to main guide →](../index.md)
- [Open a support ticket →](https://hpc.utdallas.edu/services)