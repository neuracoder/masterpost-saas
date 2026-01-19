import { ReactNode } from "react"
import { AlertTriangle, CheckCircle, Info, Lightbulb, XCircle } from "lucide-react"

interface BlogContentProps {
  children: ReactNode
}

export default function BlogContent({ children }: BlogContentProps) {
  return (
    <article className="prose prose-lg max-w-none prose-headings:font-bold prose-headings:text-gray-900 prose-p:text-gray-700 prose-p:leading-relaxed prose-a:text-green-600 prose-a:no-underline hover:prose-a:underline prose-strong:text-gray-900 prose-ul:text-gray-700 prose-ol:text-gray-700 prose-li:marker:text-green-500 prose-blockquote:border-l-green-500 prose-blockquote:bg-green-50 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r-lg prose-blockquote:not-italic prose-blockquote:text-gray-700 prose-code:bg-gray-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-gray-800 prose-code:before:content-none prose-code:after:content-none prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-img:rounded-xl prose-img:shadow-lg prose-h2:mt-12 prose-h2:mb-6 prose-h3:mt-8 prose-h3:mb-4">
      {children}
    </article>
  )
}

// Callout Component
interface CalloutProps {
  type?: 'tip' | 'warning' | 'info' | 'success' | 'error'
  title?: string
  children: ReactNode
}

export function Callout({ type = 'info', title, children }: CalloutProps) {
  const styles = {
    tip: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-400',
      icon: <Lightbulb className="w-5 h-5 text-yellow-600" />,
      titleColor: 'text-yellow-800',
      defaultTitle: 'Pro Tip'
    },
    warning: {
      bg: 'bg-orange-50',
      border: 'border-orange-400',
      icon: <AlertTriangle className="w-5 h-5 text-orange-600" />,
      titleColor: 'text-orange-800',
      defaultTitle: 'Warning'
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-400',
      icon: <Info className="w-5 h-5 text-blue-600" />,
      titleColor: 'text-blue-800',
      defaultTitle: 'Note'
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-400',
      icon: <CheckCircle className="w-5 h-5 text-green-600" />,
      titleColor: 'text-green-800',
      defaultTitle: 'Success'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-400',
      icon: <XCircle className="w-5 h-5 text-red-600" />,
      titleColor: 'text-red-800',
      defaultTitle: 'Important'
    }
  }

  const style = styles[type]

  return (
    <div className={`${style.bg} border-l-4 ${style.border} p-4 my-6 rounded-r-lg not-prose`}>
      <div className="flex items-start gap-3">
        {style.icon}
        <div>
          <p className={`font-bold ${style.titleColor} mb-1`}>
            {title || style.defaultTitle}
          </p>
          <div className="text-gray-700 text-sm leading-relaxed">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}

// Comparison Table Component
interface ComparisonRow {
  wrong: string
  right: string
}

interface ComparisonTableProps {
  rows: ComparisonRow[]
}

export function ComparisonTable({ rows }: ComparisonTableProps) {
  return (
    <div className="overflow-x-auto my-8 not-prose">
      <table className="w-full border-collapse rounded-xl overflow-hidden shadow-lg">
        <thead>
          <tr>
            <th className="bg-red-100 text-red-800 px-6 py-4 text-left font-bold">
              <span className="flex items-center gap-2">
                <XCircle className="w-5 h-5" />
                Wrong
              </span>
            </th>
            <th className="bg-green-100 text-green-800 px-6 py-4 text-left font-bold">
              <span className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Right
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
              <td className="px-6 py-4 border-t border-gray-200 text-gray-700">
                {row.wrong}
              </td>
              <td className="px-6 py-4 border-t border-gray-200 text-gray-700">
                {row.right}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// Code Block Component
interface CodeBlockProps {
  language?: string
  children: string
}

export function CodeBlock({ language = 'bash', children }: CodeBlockProps) {
  return (
    <div className="my-6 not-prose">
      <div className="bg-gray-800 rounded-t-lg px-4 py-2 flex items-center justify-between">
        <span className="text-xs text-gray-400 font-mono uppercase">{language}</span>
      </div>
      <pre className="bg-gray-900 rounded-b-lg p-4 overflow-x-auto">
        <code className="text-sm text-gray-100 font-mono">
          {children}
        </code>
      </pre>
    </div>
  )
}

// Specs Table Component
interface SpecRow {
  spec: string
  requirement: string
  notes?: string
}

interface SpecsTableProps {
  title?: string
  rows: SpecRow[]
}

export function SpecsTable({ title, rows }: SpecsTableProps) {
  return (
    <div className="my-8 not-prose">
      {title && (
        <h4 className="text-lg font-bold text-gray-900 mb-3">{title}</h4>
      )}
      <div className="overflow-x-auto rounded-xl shadow-lg">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-green-600 text-white">
              <th className="px-4 py-3 text-left font-semibold">Specification</th>
              <th className="px-4 py-3 text-left font-semibold">Requirement</th>
              {rows.some(r => r.notes) && (
                <th className="px-4 py-3 text-left font-semibold">Notes</th>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                <td className="px-4 py-3 border-t border-gray-200 font-medium text-gray-900">
                  {row.spec}
                </td>
                <td className="px-4 py-3 border-t border-gray-200 text-gray-700">
                  {row.requirement}
                </td>
                {rows.some(r => r.notes) && (
                  <td className="px-4 py-3 border-t border-gray-200 text-gray-600 text-sm">
                    {row.notes || '-'}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
