param([string]$InputPath,[string]$OutputPath,[double]$Tolerance=0.01)
$ErrorActionPreference='Stop'
try {
 Add-Type -AssemblyName PresentationCore
 Add-Type -AssemblyName WindowsBase
 $culture=[System.Globalization.CultureInfo]::InvariantCulture
 $shapes=[System.IO.File]::ReadAllText($InputPath,[System.Text.Encoding]::UTF8) | ConvertFrom-Json
 $result=[System.Windows.Media.Geometry]::Empty
 foreach ($shape in $shapes) {
  if ([string]::IsNullOrWhiteSpace($shape.path)) {continue}
  $prefix=if ($shape.evenodd) {'F0 '} else {'F1 '}
  $geometry=[System.Windows.Media.Geometry]::Parse($prefix + $shape.path)
  if ($shape.type -eq 's') {
   $pen=New-Object System.Windows.Media.Pen ([System.Windows.Media.Brushes]::Black,[double]$shape.width)
   $pen.StartLineCap=[System.Windows.Media.PenLineCap]::Round
   $pen.EndLineCap=[System.Windows.Media.PenLineCap]::Round
   $pen.LineJoin=[System.Windows.Media.PenLineJoin]::Round
   $geometry=$geometry.GetWidenedPathGeometry($pen,$Tolerance,[System.Windows.Media.ToleranceType]::Absolute)
  }
  $mode=if($shape.white){[System.Windows.Media.GeometryCombineMode]::Union}else{[System.Windows.Media.GeometryCombineMode]::Exclude}
  $result=[System.Windows.Media.Geometry]::Combine($result,$geometry,$mode,$null,$Tolerance,[System.Windows.Media.ToleranceType]::Absolute)
 }
 $path=$result.GetFlattenedPathGeometry($Tolerance,[System.Windows.Media.ToleranceType]::Absolute)
 $path.FillRule=[System.Windows.Media.FillRule]::EvenOdd
 $data=$path.ToString($culture) -replace '^\s*F[01]\s*',''
 [System.IO.File]::WriteAllText($OutputPath,$data,(New-Object System.Text.UTF8Encoding $false))
} catch { [Console]::Error.WriteLine($_.Exception.ToString()); exit 1 }
