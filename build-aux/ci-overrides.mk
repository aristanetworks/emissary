# CI overrides for docker.mk rules
# This file is included AFTER builder.mk so that these rules override the ones from docker.mk
# This allows us to prevent actual pushes to the dummy registry in CI local mode

ifdef CI_LOCAL_MODE
  # Override the .docker.tag.remote rule to skip actual tagging
  %.docker.tag.remote: %.docker $(tools/write-dockertagfile) FORCE
	@printf "$(CYN)==> $(YEL)Skipping remote tag (CI local mode)$(END)\n"
	printf '%s\n' $$(cat $<) $(docker.tag.remote) | $(tools/write-dockertagfile) $@

  # Override the .docker.push.remote rule to skip actual pushing
  %.docker.push.remote: %.docker.tag.remote FORCE
	@printf "$(CYN)==> $(YEL)Skipping remote push (CI local mode)$(END)\n"
	cp $< $@
endif

