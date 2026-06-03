import { CTA_PILL_CLASS } from '../cta'

export default function Volunteer({ data }) {
  const volunteer = data?.volunteer || {
    title: 'Be a Bandhu',
    tagline: 'Do you like to work for a social cause? You are welcome to join our team as a volunteer.',
  }
  return (
    <section id="volunteer" className="landing-section relative overflow-hidden bg-slate-100/95">
      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 text-center">
        <h2 className="font-heading font-extrabold text-3xl sm:text-4xl md:text-5xl mb-6 text-[#0b3540]">
          {volunteer.title}
        </h2>
        <p className="font-body text-lg sm:text-xl text-slate-600 leading-relaxed mb-10">
          {volunteer.tagline}
        </p>
        <a href="#" role="button" className={`auth-open-signup-modal ${CTA_PILL_CLASS}`}>
          Be a Bandhu
        </a>
      </div>
    </section>
  )
}
