import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const out = fileURLToPath(new URL('../outputs/', import.meta.url));
await fs.mkdir(out, { recursive: true });
const p = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const navy = '#102A43', blue = '#1F7A8C', pale = '#F3F7FA', gray = '#52606D';
const slides = [
  ['SmartEnergy Analytics','A cloud-ready platform for electricity consumption analysis, anomaly detection, and demand forecasting','Big Data Analytics project'],
  ['The problem','Electricity records become difficult to inspect as volume grows. Users need one workflow for cleaning, trends, peaks, unusual readings, future demand, and evidence-backed insights.','Historical data is the initial scope.'],
  ['System architecture','Source CSV or S3 raw object → validation and feature engineering → PySpark processing path → analytical outputs → Streamlit and Plotly dashboard','Boto3 uses the standard AWS credential chain.'],
  ['Processing workflow','Schema checks and UTC timestamp parsing\nCalendar features and entity keys\nHourly, daily, monthly, and entity summaries\nCSV exports and quality metadata','The pipeline records the engine that actually ran.'],
  ['Analytics modules','Consumption: peaks, trends, comparisons\nAnomalies: prior rolling baseline and z-score\nForecasting: seven-day historical mean baseline\nInsights: generated from measured outputs','An anomaly is a candidate for investigation, not a confirmed fault.'],
  ['Dashboard pages','Energy overview\nConsumption analytics\nAnomaly monitor\nDemand forecast\nEnergy insights\nData quality and performance','The dashboard reads processed outputs instead of fabricating metrics.'],
  ['Demonstration results','Included demo: 2,016 synthetic hourly records, zero invalid rows, zero duplicate removals, zero missing values\nAutomated tests: 3 passed\nStreamlit smoke test: HTTP 200','Demo data is synthetic and clearly labeled.'],
  ['Evaluation and next steps','Measured benchmark runner for increasing dataset sizes\nSecure S3 integration ready for a real bucket\nPublic GitHub repository with reproducible setup\nNext academic step: substitute and document a public dataset','Spark and S3 results remain environment-dependent until a supported runtime and credentials are used.'],
];
for (let i=0;i<slides.length;i++) {
  const s=p.slides.add(); s.background.fill = i===0 ? navy : pale;
  const title=s.shapes.add({geometry:'textbox',position:{left:72,top:70,width:1136,height:72},fill:'none',line:{style:'solid',fill:'none',width:0}}); title.text=slides[i][0]; title.text.style={fontSize:i===0?48:38,bold:true,color:i===0?'#FFFFFF':navy};
  const body=s.shapes.add({geometry:'textbox',position:{left:96,top:190,width:1080,height:250},fill:'none',line:{style:'solid',fill:'none',width:0}}); body.text=slides[i][1]; body.text.style={fontSize:i===0?28:25,color:i===0?'#E6F6F8':navy};
  const foot=s.shapes.add({geometry:'textbox',position:{left:96,top:560,width:1000,height:60},fill:'none',line:{style:'solid',fill:'none',width:0}}); foot.text=slides[i][2]; foot.text.style={fontSize:18,color:i===0?'#9FB3C8':gray};
  const bar=s.shapes.add({geometry:'rect',position:{left:72,top:155,width:150,height:8},fill:i===0?blue:blue,line:{style:'solid',fill:'none',width:0}});
  const num=s.shapes.add({geometry:'textbox',position:{left:1120,top:650,width:80,height:30},fill:'none',line:{style:'solid',fill:'none',width:0}}); num.text=String(i+1).padStart(2,'0'); num.text.style={fontSize:16,bold:true,color:i===0?'#9FB3C8':gray};
}
const pptx=await PresentationFile.exportPptx(p); await pptx.save(out+'\\SmartEnergy-Analytics-Demonstration.pptx');
