Sub setUpVBCallback(flashId)
	ExecuteGlobal "Sub " & flashId & _
	    "_FSCommand(ByVal command, ByVal args)" & _
 		"FlashProxy.callJS command, args" & vbcrlf & _
 		"End Sub"
End Sub