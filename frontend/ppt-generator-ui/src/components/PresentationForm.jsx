import React from 'react';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from './ui/form';
import { useForm } from 'react-hook-form';
import { ThemePreview } from './theme-preview';
import { useTheme } from '../context/theme-context.jsx';

const PresentationForm = ({
  onSubmit,
  isGenerating,
  defaultValues = {
    title: '',
    description: '',
    numSlides: 5,
    theme: 'modern',
  },
}) => {
  const { availableThemes } = useTheme();
  const form = useForm({
    defaultValues,
  });

  const handleSubmit = (data) => {
    onSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-8">
        <Card className="p-6">
          <div className="space-y-6">
            {/* Title field */}
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Presentation Topic/Title</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter your presentation topic or title"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    This will be used to generate the presentation content
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Description field */}
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Additional Details (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add any specific requirements or additional information"
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Include any specific points you want to cover or style preferences
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Number of slides field */}
            <FormField
              control={form.control}
              name="numSlides"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Number of Slides</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={3}
                      max={20}
                      {...field}
                      value={field.value || ''}
                      onChange={(e) => {
                        const value = e.target.value === '' ? '' : parseInt(e.target.value, 10);
                        field.onChange(value || 5); // Default to 5 if value is invalid
                      }}
                    />
                  </FormControl>
                  <FormDescription>
                    Recommended: 5-10 slides for a concise presentation
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Theme selection */}
            <FormField
              control={form.control}
              name="theme"
              render={({ field }) => (
                <FormItem className="space-y-4">
                  <FormLabel>Select Theme</FormLabel>
                  <FormControl>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {availableThemes.map((theme) => (
                        <ThemePreview
                          key={theme.id}
                          theme={theme}
                          name={theme.name}
                          isActive={field.value === theme.id}
                          onSelect={() => field.onChange(theme.id)}
                        />
                      ))}
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="mt-8">
            <Button
              type="submit"
              className="w-full"
              disabled={isGenerating}
            >
              {isGenerating ? 'Generating Presentation...' : 'Generate Presentation'}
            </Button>
          </div>
        </Card>
      </form>
    </Form>
  );
};

export default PresentationForm;
