<script setup>
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const instruments = ref([])
const result = ref(null)
const error = ref('')
const loading = ref(false)
const percentage = value => `${(value * 100).toFixed(2)}%`

onMounted(async () => {
  instruments.value = await fetch('/instruments').then(r => r.json())
})

async function runBacktest() {
  loading.value = true; error.value = ''
  const response = await fetch('/backtests', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
    symbols: instruments.value.map(x => x.symbol), start_date:'2025-01-02', end_date:'2025-01-17', short_window:3, long_window:5
  })})
  const body = await response.json(); loading.value = false
  if (!response.ok) { error.value = body.detail ?? '回测失败'; return }
  result.value = body
  await nextTick()
  const chart = echarts.init(document.querySelector('#equity-chart'))
  let peak = -Infinity
  const drawdown = body.equity.map(x => { peak = Math.max(peak, x.total_equity); return x.total_equity / peak - 1 })
  chart.setOption({tooltip:{trigger:'axis'},legend:{data:['总权益','回撤']},xAxis:{type:'category',data:body.equity.map(x=>x.trading_date)},yAxis:[{type:'value',scale:true,name:'权益（元）'},{type:'value',name:'回撤',axisLabel:{formatter:v=>(v*100).toFixed(0)+'%'}}],series:[{name:'总权益',type:'line',data:body.equity.map(x=>x.total_equity),smooth:true},{name:'回撤',type:'line',yAxisIndex:1,data:drawdown,areaStyle:{},color:'#c0392b'}]})
}
</script>

<template>
  <main><h1>Quant Lab 中国 A 股教学平台</h1>
    <p class="warning">仅用于研究、回测和模拟盘，不连接券商，不构成投资建议。</p>
    <section class="grid"><article><h2>股票池</h2><p>{{ instruments.map(x=>x.symbol+' '+x.name).join('、') }}</p></article><article><h2>策略</h2><p>3 日 / 5 日双均线，下一开盘执行</p></article><article><h2>模式</h2><p>离线教学数据</p></article></section>
    <button :disabled="loading" @click="runBacktest">{{ loading ? '运行中…' : '运行受约束回测' }}</button><p class="error">{{ error }}</p>
    <section v-if="result"><h2>回测 #{{ result.id }}</h2>
      <div class="metrics"><span>总收益 {{ percentage(result.metrics.total_return) }}</span><span>最大回撤 {{ percentage(result.metrics.max_drawdown) }}</span><span>Sharpe {{ result.metrics.sharpe.toFixed(2) }}</span><span>成交 {{ result.fills.length }} 笔</span></div>
      <div id="equity-chart"></div>
      <h3>成交记录</h3><table><thead><tr><th>日期</th><th>代码</th><th>方向</th><th>数量</th><th>价格</th><th>费用</th></tr></thead><tbody><tr v-for="(fill,index) in result.fills" :key="index"><td>{{ fill.trading_date }}</td><td>{{ fill.symbol }}</td><td>{{ fill.side }}</td><td>{{ fill.quantity }}</td><td>{{ fill.price.toFixed(3) }}</td><td>{{ (fill.commission+fill.tax).toFixed(2) }}</td></tr></tbody></table>
    </section>
  </main>
</template>
