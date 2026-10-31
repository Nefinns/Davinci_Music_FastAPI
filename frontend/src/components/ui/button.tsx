import { Button as BaseButton } from '@base-ui/react/button'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import type { ComponentProps } from 'react'

const variants = cva('inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#C8A04A] disabled:opacity-55 disabled:cursor-not-allowed', {
  variants: {
    variant: {
      primary: 'bg-[#0A3D3A] text-white hover:bg-[#12544F]',
      accent: 'bg-[#C8A04A] text-[#14181B] hover:bg-[#DBB35F]',
      outline: 'border border-[#D7DFDB] bg-white text-[#263B36] hover:bg-[#EDF3F0]',
      subtle: 'bg-transparent text-[#41645E] hover:bg-[#E9F0EB]'
    },
    size: { sm: 'px-3 py-2 text-sm', md: 'px-4 py-2.5 text-sm', lg: 'px-5 py-3 text-base' }
  },
  defaultVariants: {variant: 'primary', size: 'md'}
})

type Props = ComponentProps<typeof BaseButton> & VariantProps<typeof variants>
export function Button({className, variant, size, ...props}: Props) {
  return <BaseButton className={cn(variants({variant, size}), className)} {...props}/>
}
