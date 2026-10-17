import { useTranslation } from 'react-i18next'
import Icon from './Icon'

/**
 * "This is education, not advice" — on every screen that states a figure.
 *
 * It used to live on the recommendation screen alone, plus a one-time modal
 * at onboarding. But Holdings values someone's property and tells them their
 * mix has drifted; Explore returns a rent-or-buy verdict and a price
 * judgement on a specific listing; the Dashboard splits a budget. Those are
 * the screens a reader acts on, and none of them said what the numbers were
 * and were not.
 *
 * It is also the app's position in one sentence. Apple asks that apps in
 * "financial services" come from the institution providing them
 * (5.1.1(ix), 3.2.1(viii)); Lumos executes nothing, holds nothing and
 * recommends nothing personal, and the place that claim has to be visible
 * is the product itself rather than a note in a console.
 *
 * `variant="projection"` for screens showing a future band, where the
 * sentence that matters is a different one: this is a distribution of what
 * already happened, not a forecast.
 */
export default function Disclaimer({ variant = 'default' }) {
  const { t } = useTranslation()
  return (
    <div className="disclaimer">
      <Icon name="warning" size={13} />{' '}
      {t(variant === 'projection' ? 'common.disclaimerProjection' : 'common.disclaimer')}
    </div>
  )
}
