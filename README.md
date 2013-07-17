git-notify
==========

Push driven update notification (hook script)

# Install
git-notify scirpt installs `hooks/post-receive` script into your git bare repository 

`cd foo.git`  
`git-notify install`  

# Notification
Notification will be sent to all committers if your commit message starts from '@'

`git commit -m "@Your notification"`  
`git push origin master`  

if your message body includes <...@...> like email addresses, 
notification will be also sent to those addresses.
