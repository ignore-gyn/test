Function sayHelloWorld() As String()

    Dim testArr(1) As String

    testArr(0) = "Hello"
    testArr(1) = "World"

    sayHelloWorld = testArr
End Function


Set ThisWorksheet = ActiveSheet
'''''''''''''''''''''''''''
' Excel�̉��s�R�[�h��chr(10)�炵���̂ŕs�v����?
buf2 = Replace(buf1, vbLf, vbCrLf)
'''''''''''''''''''''''''''

On Error GoTo ErrorHandler

' 0-512�͗\��ς�
Call Err.Raise(1234, Me.Name, "�G���[�����B�R�m�����[")
' Me�̓N���X���W���[���ł����g���Ȃ�
Call Err.Raise(1234)
' �����ł��ǂ��Asource��string

'On Error Resume Next

ErrorHandler:
 
    ' �G���[�ԍ��ƃG�����b�Z�[�W���o��
    MsgBox Err.Number & ":" & Err.Source & ":" & Err.Description
 
    ' �G���[���N���A����
    Err.Clear
'''''''''''''''''''''''''''
Dim arr() As String
ReDim arr(2)
ReDim Preserve arr(3)	'�����܂ł̕ҏW���e���c��
ReDim arr(4)	'�����܂ł̕ҏW���e��������
'''''''''''''''''''''''''''
'Dim i1() As Integer = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}  # VB
Dim i1() As Variant
i1 = Array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
Dim i2() As Integer = Array.CreateInstance(GetType(Integer), 8)
' Dim i2(8) As Integer


Array.Copy(i1, 0, i2, 0, 6)
' i2: {0, 1, 2, 3, 4, 5}
'''''''''''''''''''''''''''


Dim list As New Collection

list.Add "hoge"
list.Add "fuga"

' Index��1�n�܂�
Debug.Print list(1)
Debug.Print list.Item(2)

For i = 1 To list.Count
    Debug.Print (i & " : " & list(i))
Next

Dim e As Variant

For Each e In list
    Debug.Print e
Next

	"ceid_filter": [
		{
			"CEID": xxxxxx,
			"VID": []
		},
		{
			"CEID": xxxxxx,
			"VID": [
				zzzz
			]
		},
		{
			"CEID": xxxxxx,
			"VID": [
				yyyy,
				zzzz
			]
		}
	]
