## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1488 | 0.40 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0234 | 0.33 | ❌ rejected |
| 6 | approach → descend → grasp → lift → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.1916 | 0.16 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0927 | 0.35 | ❌ rejected |
| 4 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.3226 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.149) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_object
  target_entity: object
  weight: 0.2
phases:
- id: approach_above_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descent_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: lift_object
- id: approach_above_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.149
- **task_score** (E): 0.403
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0736 |
| descend_to_grasp | 1.00 | 1.00 | 0.1997 |
| grasp | 1.00 | 1.00 | 0.0116 |
| lift | 1.00 | 1.00 | 0.2406 |
| approach_above_goal | 1.00 | 1.00 | 0.2443 |
| descend_to_place | 1.00 | 1.00 | 0.1653 |
| release | 1.00 | 1.00 | 0.0196 |
| retract_from_goal | 1.00 | 1.00 | 0.1354 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.010, 0.234) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 14.237 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.494, -0.010, 0.234)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.137 | 0.192 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.478, -0.015, 0.267) | (0.493, -0.015, 0.026)→(0.488, -0.015, 0.260) | 0.281→0.259 | 1.00 / 41.000 | 0.072 | 0.654 |
| approach_above_goal | approach | 1.00 / step_budget | (0.478, -0.015, 0.267)→(0.626, 0.164, 0.338) | (0.488, -0.015, 0.260)→(0.627, 0.164, 0.315) | 0.259→0.151 | 1.00 / 35.667 | 0.090 | 0.157 |
| descend_to_place | descend | 1.00 / step_budget | (0.626, 0.164, 0.338)→(0.632, 0.173, 0.173) | (0.627, 0.164, 0.315)→(0.621, 0.172, 0.146) | 0.151→0.025 | 1.00 / 25.000 | 0.114 | 0.219 |
| release | release | 1.00 / step_budget | (0.632, 0.173, 0.173)→(0.626, 0.171, 0.192) | (0.621, 0.172, 0.146)→(0.615, 0.171, 0.025) | 0.025→0.141 | 1.00 / 4.000 | 0.097 | 1.474 |
| retract_from_goal | retract | 1.00 / step_budget | (0.626, 0.171, 0.192)→(0.624, 0.170, 0.327) | (0.615, 0.171, 0.025)→(0.614, 0.172, 0.026) | 0.141→0.141 | 1.00 / 4.000 | 0.123 | 0.139 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.548
- phase_score: 0.503
- phase_breakdown.approach_object_score: 0.487
- phase_breakdown.grasp_object_score: 0.794
- phase_breakdown.lift_object_score: 0.747
- phase_breakdown.approach_goal_score: 0.456
- phase_breakdown.place_object_score: 0.031
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.548
- **Median Q (composite search score)**: -0.183
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.289


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29243,"average_solve_count":383.0,"average_success_count":383.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.19575,"approach_above_goal.approach_goal_speed":0.09422,"approach_above_object.approach_height":0.23109,"approach_above_object.approach_speed":0.1562,"descend_to_grasp.descent_speed":0.05942,"descend_to_grasp.grasp_z_tolerance":0.0133,"descend_to_place.place_speed":0.06518,"descend_to_place.place_z_tolerance":0.01267,"lift.lift_height":0.27104,"lift.lift_speed":0.03676,"lift.lift_tolerance":0.01859,"retract_from_goal.retract_height":0.14851,"retract_from_goal.retract_speed":0.07497},"optimized_scores":{"best_composite_score":-0.183,"best_fitness_score":0.647,"best_task_score":0.33147},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":226.0,"contact_point_centroid":[0.60819,0.15905,-0.00674],"force_p95":1.00872,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76245,"mean_force":0.318,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62163,0.15555,0.20894]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47201,-0.0192,-0.00145],"force_p95":0.61793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63877,"mean_force":0.24879,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4635,-0.01935,0.0284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16328.0,"contact_point_centroid":[0.46135,-0.0001,0.15267],"force_p95":0.07453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27675,"mean_force":0.05224,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46121,-0.01927,0.15048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17106.0,"contact_point_centroid":[0.46128,-0.03838,0.15603],"force_p95":0.07328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27524,"mean_force":0.05039,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46122,-0.01927,0.15406]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01998,-0.00207],"force_p95":0.14327,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20597,"mean_force":0.12828,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4656,-0.01939,0.02839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9027.0,"contact_point_centroid":[0.62334,0.17123,0.29561],"force_p95":0.09212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20119,"mean_force":0.05656,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62335,0.15224,0.29427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.62469,0.17576,0.19304],"force_p95":0.09568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19737,"mean_force":0.06041,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62517,0.15668,0.19401]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8799.0,"contact_point_centroid":[0.62306,0.1334,0.28937],"force_p95":0.08979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19394,"mean_force":0.05848,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62359,0.15257,0.28764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.62378,0.13784,0.1936],"force_p95":0.08615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1876,"mean_force":0.05474,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62522,0.15669,0.1941]},{"body_a":"world","body_b":"grasp_target","contact_count":3692.0,"contact_point_centroid":[0.60819,0.15881,-0.00198],"force_p95":0.12374,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14331,"mean_force":0.12194,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.6193,0.15478,0.28385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15000.0,"contact_point_centroid":[0.53806,0.0432,0.32302],"force_p95":0.08198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14151,"mean_force":0.05227,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53812,0.06239,0.32184]},{"body_a":"world","body_b":"grasp_target","contact_count":260.0,"contact_point_centroid":[0.47616,-0.02015,-0.00151],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12474,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49345,-0.00467,0.28928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.46446,-0.00015,0.02958],"force_p95":0.06826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12718,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.01937,0.0273]},{"body_a":"world","body_b":"grasp_target","contact_count":3216.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12322,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47775,-0.01515,0.15347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15538.0,"contact_point_centroid":[0.54242,0.08579,0.3255],"force_p95":0.07188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11474,"mean_force":0.04931,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.54225,0.06672,0.32432]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5181.0,"contact_point_centroid":[0.46432,-0.0386,0.02911],"force_p95":0.06705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08025,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.01937,0.0273]}],"total_contact_groups":16},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60819,0.15881,0.02602],"final_tcp_position":[0.62011,0.15493,0.35108],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.76245,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02589],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12337,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":260.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48565,-0.0108,0.2756],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02589],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28846,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3216.0,"raw_peak_contact_force":0.12322,"subtask_id":"grasp_object","tcp_end":[0.47231,-0.01953,0.03506],"tcp_start":[0.48565,-0.0108,0.2756],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01941,0.02575],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28814,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14013,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11792.0,"raw_peak_contact_force":0.20597,"subtask_id":"grasp_object","tcp_end":[0.46445,-0.01936,0.02727],"tcp_start":[0.47231,-0.01953,0.03506],"tcp_to_object_dist_end":0.01168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.47162,-0.01929,0.27114],"object_pos_start":[0.47603,-0.01941,0.02575],"object_to_goal_dist_end":0.25293,"object_to_goal_dist_start":0.28814,"object_z_max":0.27085,"peak_contact_force":0.0714,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33516.0,"raw_peak_contact_force":0.63877,"subtask_id":"lift_object","tcp_end":[0.46196,-0.01929,0.27851],"tcp_start":[0.46445,-0.01936,0.02727],"tcp_to_object_dist_end":0.01216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.62417,0.14841,0.35126],"object_pos_start":[0.47162,-0.01929,0.27114],"object_to_goal_dist_end":0.16177,"object_to_goal_dist_start":0.25293,"object_z_max":0.3512,"peak_contact_force":0.09539,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30538.0,"raw_peak_contact_force":0.14151,"subtask_id":"approach_goal","tcp_end":[0.62118,0.14875,0.37212],"tcp_start":[0.46196,-0.01929,0.27851],"tcp_to_object_dist_end":0.02108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.61612,0.15679,0.17415],"object_pos_start":[0.62417,0.14841,0.35126],"object_to_goal_dist_end":0.02217,"object_to_goal_dist_start":0.16177,"object_z_max":0.35126,"peak_contact_force":0.09996,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17826.0,"raw_peak_contact_force":0.20119,"subtask_id":"place_object","tcp_end":[0.6271,0.15719,0.1986],"tcp_start":[0.62118,0.14875,0.37212],"tcp_to_object_dist_end":0.02681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60915,0.15676,0.02494],"object_pos_start":[0.61612,0.15679,0.17415],"object_to_goal_dist_end":0.16659,"object_to_goal_dist_start":0.02217,"object_z_max":0.17415,"peak_contact_force":0.08046,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2118.0,"raw_peak_contact_force":1.76245,"subtask_id":"place_object","tcp_end":[0.6216,0.15554,0.21748],"tcp_start":[0.6271,0.15719,0.1986],"tcp_to_object_dist_end":0.19295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.60819,0.15881,0.02602],"object_pos_start":[0.60915,0.15676,0.02494],"object_to_goal_dist_end":0.16563,"object_to_goal_dist_start":0.16659,"object_z_max":0.02666,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3692.0,"raw_peak_contact_force":0.14331,"subtask_id":"place_object","tcp_end":[0.62011,0.15493,0.35108],"tcp_start":[0.6216,0.15554,0.21748],"tcp_to_object_dist_end":0.3253,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58863,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.17561,"approach_above_goal.approach_goal_speed":0.13676,"approach_above_object.approach_height":0.16738,"approach_above_object.approach_speed":0.1625,"descend_to_grasp.descent_speed":0.08544,"descend_to_grasp.grasp_z_tolerance":0.00909,"descend_to_place.place_speed":0.07255,"descend_to_place.place_z_tolerance":0.01264,"lift.lift_height":0.21842,"lift.lift_speed":0.04236,"lift.lift_tolerance":0.01987,"retract_from_goal.retract_height":0.16234,"retract_from_goal.retract_speed":0.09696},"optimized_scores":{"best_composite_score":-0.07438,"best_fitness_score":0.75562,"best_task_score":0.54781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":338.0,"contact_point_centroid":[0.61098,0.20363,-0.0039],"force_p95":0.61245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98798,"mean_force":0.20048,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6179,0.20299,0.12827]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.45441,-0.02538,-0.00146],"force_p95":0.60436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62628,"mean_force":0.25175,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44632,-0.02546,0.02899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":782.0,"contact_point_centroid":[0.62188,0.22326,0.11394],"force_p95":0.10719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2941,"mean_force":0.07128,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62235,0.20466,0.11721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":713.0,"contact_point_centroid":[0.62116,0.18586,0.11474],"force_p95":0.11549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28277,"mean_force":0.07512,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62236,0.20466,0.11723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12990.0,"contact_point_centroid":[0.4442,-0.0445,0.12832],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26064,"mean_force":0.05145,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44399,-0.02535,0.12646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12992.0,"contact_point_centroid":[0.44418,-0.0062,0.12836],"force_p95":0.07325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24789,"mean_force":0.0512,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44399,-0.02535,0.12645]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00207],"force_p95":0.14381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21052,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44836,-0.02553,0.02895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7160.0,"contact_point_centroid":[0.62005,0.21857,0.20858],"force_p95":0.11081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18183,"mean_force":0.0646,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62065,0.19982,0.20866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6358.0,"contact_point_centroid":[0.61948,0.18075,0.2077],"force_p95":0.11928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17108,"mean_force":0.07214,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62071,0.19991,0.20743]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.45856,-0.02632,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48313,-0.00971,0.25884]},{"body_a":"world","body_b":"grasp_target","contact_count":3720.0,"contact_point_centroid":[0.61099,0.20358,-0.00199],"force_p95":0.12294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13127,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61473,0.20177,0.21365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.44667,-0.00624,0.02948],"force_p95":0.06554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12954,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44728,-0.02549,0.02794]},{"body_a":"world","body_b":"grasp_target","contact_count":2320.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4588,-0.02311,0.12385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17294.0,"contact_point_centroid":[0.53117,0.10545,0.25338],"force_p95":0.0739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11925,"mean_force":0.0468,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53135,0.0864,0.25118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15099.0,"contact_point_centroid":[0.53158,0.06808,0.25341],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11532,"mean_force":0.05332,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53212,0.08733,0.25143]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5433.0,"contact_point_centroid":[0.44668,-0.04479,0.02934],"force_p95":0.0656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08076,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44729,-0.02549,0.02794]}],"total_contact_groups":16},"final_pose_error":0.01552,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61099,0.20358,0.02602],"final_tcp_position":[0.61555,0.20197,0.28755],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":42.46398,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":175.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":42.46398,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":696.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46521,-0.02058,0.21484],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2320.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45489,-0.02575,0.03517],"tcp_start":[0.46521,-0.02058,0.21484],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02557,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14109,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12520.0,"raw_peak_contact_force":0.21052,"subtask_id":"grasp_object","tcp_end":[0.44726,-0.02549,0.02791],"tcp_start":[0.45489,-0.02575,0.03517],"tcp_to_object_dist_end":0.0114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.45389,-0.02536,0.22056],"object_pos_start":[0.45844,-0.02557,0.02574],"object_to_goal_dist_end":0.31137,"object_to_goal_dist_start":0.30322,"object_z_max":0.22027,"peak_contact_force":0.07293,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26064.0,"raw_peak_contact_force":0.62628,"subtask_id":"lift_object","tcp_end":[0.44437,-0.02535,0.22668],"tcp_start":[0.44726,-0.02549,0.02791],"tcp_to_object_dist_end":0.01131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.61701,0.19639,0.25625],"object_pos_start":[0.45389,-0.02536,0.22056],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.31137,"object_z_max":0.25624,"peak_contact_force":0.07388,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32393.0,"raw_peak_contact_force":0.11925,"subtask_id":"approach_goal","tcp_end":[0.61918,0.19616,0.27838],"tcp_start":[0.44437,-0.02535,0.22668],"tcp_to_object_dist_end":0.02224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.61325,0.20503,0.09561],"object_pos_start":[0.61701,0.19639,0.25625],"object_to_goal_dist_end":0.02525,"object_to_goal_dist_start":0.14323,"object_z_max":0.25625,"peak_contact_force":0.12134,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13518.0,"raw_peak_contact_force":0.18183,"subtask_id":"place_object","tcp_end":[0.62478,0.20545,0.122],"tcp_start":[0.61918,0.19616,0.27838],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61099,0.20356,0.02637],"object_pos_start":[0.61325,0.20503,0.09561],"object_to_goal_dist_end":0.08994,"object_to_goal_dist_start":0.02525,"object_z_max":0.09561,"peak_contact_force":0.12766,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1833.0,"raw_peak_contact_force":0.98798,"subtask_id":"place_object","tcp_end":[0.61778,0.20294,0.14054],"tcp_start":[0.62478,0.20545,0.122],"tcp_to_object_dist_end":0.11437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.61099,0.20358,0.02602],"object_pos_start":[0.61099,0.20356,0.02637],"object_to_goal_dist_end":0.09027,"object_to_goal_dist_start":0.08994,"object_z_max":0.02637,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.13127,"subtask_id":"place_object","tcp_end":[0.61555,0.20197,0.28755],"tcp_start":[0.61778,0.20294,0.14054],"tcp_to_object_dist_end":0.26158,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31138,"average_solve_count":334.0,"average_success_count":334.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.18773,"approach_above_goal.approach_goal_speed":0.11627,"approach_above_object.approach_height":0.16599,"approach_above_object.approach_speed":0.16386,"descend_to_grasp.descent_speed":0.05986,"descend_to_grasp.grasp_z_tolerance":0.01031,"descend_to_place.place_speed":0.07736,"descend_to_place.place_z_tolerance":0.01284,"lift.lift_height":0.29141,"lift.lift_speed":0.05055,"lift.lift_tolerance":0.02482,"retract_from_goal.retract_height":0.16113,"retract_from_goal.retract_speed":0.06096},"optimized_scores":{"best_composite_score":-0.18889,"best_fitness_score":0.64111,"best_task_score":0.32841},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":222.0,"contact_point_centroid":[0.62262,0.15366,-0.0066],"force_p95":1.02386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6721,"mean_force":0.32099,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63797,0.15437,0.20949]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.53976,0.00071,-0.00141],"force_p95":0.65728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69672,"mean_force":0.23025,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52866,0.00083,0.025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18422.0,"contact_point_centroid":[0.527,-0.01831,0.16364],"force_p95":0.0784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31,"mean_force":0.05496,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52625,0.0008,0.16154]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18889.0,"contact_point_centroid":[0.52695,0.01987,0.16025],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29808,"mean_force":0.05394,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52625,0.0008,0.15829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6519.0,"contact_point_centroid":[0.6412,0.16981,0.2796],"force_p95":0.11764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27345,"mean_force":0.07138,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64062,0.15125,0.28106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5971.0,"contact_point_centroid":[0.6415,0.13218,0.28167],"force_p95":0.12475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25488,"mean_force":0.08104,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64057,0.15116,0.28298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":672.0,"contact_point_centroid":[0.63916,0.13657,0.19165],"force_p95":0.11979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23891,"mean_force":0.0767,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64144,0.15546,0.19479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":791.0,"contact_point_centroid":[0.64075,0.17399,0.19062],"force_p95":0.10134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23497,"mean_force":0.06805,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64147,0.15547,0.19484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8723.0,"contact_point_centroid":[0.5847,0.05474,0.32895],"force_p95":0.09783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20877,"mean_force":0.06731,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58196,0.07372,0.32792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9472.0,"contact_point_centroid":[0.58467,0.09252,0.32851],"force_p95":0.09016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17476,"mean_force":0.06248,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58188,0.07367,0.32781]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16041,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53103,0.00088,0.02533]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.62267,0.15353,-0.00198],"force_p95":0.12411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14209,"mean_force":0.12197,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.63569,0.15363,0.28025]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.54431,0.00113,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.5152,0.00041,0.2568]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53406,0.00092,0.1212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53082,-0.01834,0.02659],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11023,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52978,0.00086,0.0239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53075,0.01994,0.02571],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0967,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52978,0.00086,0.0239]}],"total_contact_groups":16},"final_pose_error":0.03567,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62267,0.15353,0.02602],"final_tcp_position":[0.63642,0.15375,0.34338],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.6721,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53246,0.00086,0.21169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18605,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53847,0.00102,0.03395],"tcp_start":[0.53246,0.00086,0.21169],"tcp_to_object_dist_end":0.00984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16041,"subtask_id":"grasp_object","tcp_end":[0.52975,0.00086,0.02386],"tcp_start":[0.53847,0.00102,0.03395],"tcp_to_object_dist_end":0.01454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.53926,0.00082,0.28722],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.21381,"object_to_goal_dist_start":0.25053,"object_z_max":0.28696,"peak_contact_force":0.07078,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37397.0,"raw_peak_contact_force":0.69672,"subtask_id":"lift_object","tcp_end":[0.52735,0.00081,0.29547],"tcp_start":[0.52975,0.00086,0.02386],"tcp_to_object_dist_end":0.01448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.64088,0.14698,0.33783],"object_pos_start":[0.53926,0.00082,0.28722],"object_to_goal_dist_end":0.1473,"object_to_goal_dist_start":0.21381,"object_z_max":0.33778,"peak_contact_force":0.10111,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18195.0,"raw_peak_contact_force":0.20877,"subtask_id":"approach_goal","tcp_end":[0.6387,0.14698,0.36485],"tcp_start":[0.52735,0.00081,0.29547],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.63364,0.15557,0.16871],"object_pos_start":[0.64088,0.14698,0.33783],"object_to_goal_dist_end":0.02652,"object_to_goal_dist_start":0.1473,"object_z_max":0.33783,"peak_contact_force":0.12219,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12490.0,"raw_peak_contact_force":0.27345,"subtask_id":"place_object","tcp_end":[0.64344,0.15597,0.19979],"tcp_start":[0.6387,0.14698,0.36485],"tcp_to_object_dist_end":0.0326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62555,0.15335,0.02477],"object_pos_start":[0.63364,0.15557,0.16871],"object_to_goal_dist_end":0.16785,"object_to_goal_dist_start":0.02652,"object_z_max":0.16871,"peak_contact_force":0.08341,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1685.0,"raw_peak_contact_force":1.6721,"subtask_id":"place_object","tcp_end":[0.63794,0.15436,0.21789],"tcp_start":[0.64344,0.15597,0.19979],"tcp_to_object_dist_end":0.19352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62267,0.15353,0.02602],"object_pos_start":[0.62555,0.15335,0.02477],"object_to_goal_dist_end":0.16702,"object_to_goal_dist_start":0.16785,"object_z_max":0.02668,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.14209,"subtask_id":"place_object","tcp_end":[0.63642,0.15375,0.34338],"tcp_start":[0.63794,0.15436,0.21789],"tcp_to_object_dist_end":0.31766,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```