import Footer from '../components/Footer.tsx'
import { gplV2Text } from '../data/GPLv2.ts'

function Licence () {
  return (
    <div>
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
            <h1>Licence</h1>
            <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                {gplV2Text}
            </pre>
        </div>

      <Footer />
    </div>
  )
}

export default Licence